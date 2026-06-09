"""DuckDB adapter — the analytical store for SELF."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb

from .api import StorageAPI
from .migration_engine import MigrationEngine
from .schema_validator import SchemaValidator


class DuckDBAdapter(StorageAPI):
    SCHEMAS: dict[str, str] = {
        "observation_event": """
            CREATE TABLE IF NOT EXISTS observation_event (
                schema_version VARCHAR NOT NULL,
                id VARCHAR PRIMARY KEY,
                event_type VARCHAR NOT NULL,
                source JSON NOT NULL,
                timestamp VARCHAR NOT NULL,
                monotonic_ts BIGINT NOT NULL,
                observed_at VARCHAR NOT NULL,
                actor JSON NOT NULL,
                subject JSON,
                payload JSON NOT NULL,
                content_hash VARCHAR NOT NULL,
                raw_ref VARCHAR,
                tags JSON,
                provenance JSON NOT NULL
            );
        """,
        "knowledge_object": """
            CREATE TABLE IF NOT EXISTS knowledge_object (
                schema_version VARCHAR NOT NULL,
                id VARCHAR PRIMARY KEY,
                type VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                description VARCHAR DEFAULT '',
                attributes JSON DEFAULT '{}',
                confidence REAL NOT NULL DEFAULT 0.5,
                provenance JSON NOT NULL,
                created_at VARCHAR NOT NULL,
                updated_at VARCHAR NOT NULL,
                deprecated BOOLEAN DEFAULT false,
                superseded_by VARCHAR
            );
        """,
        "audit_log_entry": """
            CREATE TABLE IF NOT EXISTS audit_log_entry (
                schema_version VARCHAR NOT NULL,
                id VARCHAR PRIMARY KEY,
                timestamp VARCHAR NOT NULL,
                actor VARCHAR NOT NULL,
                action VARCHAR NOT NULL,
                entity_type VARCHAR NOT NULL,
                entity_id VARCHAR NOT NULL,
                before_hash VARCHAR,
                after_hash VARCHAR,
                reason VARCHAR,
                prev_hash VARCHAR,
                metadata JSON DEFAULT '{}'
            );
        """,
        "event_log_entry": """
            CREATE TABLE IF NOT EXISTS event_log_entry (
                schema_version VARCHAR NOT NULL,
                id VARCHAR PRIMARY KEY,
                event_id VARCHAR NOT NULL,
                timestamp VARCHAR NOT NULL,
                source_kind VARCHAR NOT NULL,
                event_type VARCHAR NOT NULL,
                content_hash VARCHAR NOT NULL,
                raw_payload_ref VARCHAR
            );
        """,
        "ingest_queue": """
            CREATE TABLE IF NOT EXISTS ingest_queue (
                schema_version VARCHAR NOT NULL,
                id VARCHAR PRIMARY KEY,
                event_id VARCHAR NOT NULL,
                event JSON NOT NULL,
                priority INTEGER NOT NULL DEFAULT 1,
                queued_at DOUBLE NOT NULL,
                status VARCHAR NOT NULL DEFAULT 'queued',
                error VARCHAR
            );
        """,
        "summary": """
            CREATE TABLE IF NOT EXISTS summary (
                schema_version VARCHAR NOT NULL,
                id VARCHAR PRIMARY KEY,
                type VARCHAR NOT NULL,
                content VARCHAR NOT NULL,
                source_ids JSON,
                created_at VARCHAR NOT NULL,
                provenance JSON
            );
        """,
        "identity_node": """
            CREATE TABLE IF NOT EXISTS identity_node (
                schema_version VARCHAR NOT NULL,
                id VARCHAR PRIMARY KEY,
                type VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                aliases JSON DEFAULT '[]',
                attributes JSON DEFAULT '{}',
                created_at VARCHAR NOT NULL,
                updated_at VARCHAR NOT NULL,
                valid_from VARCHAR NOT NULL,
                valid_to VARCHAR,
                deprecated BOOLEAN DEFAULT false,
                superseded_by VARCHAR
            );
        """,
        "identity_edge": """
            CREATE TABLE IF NOT EXISTS identity_edge (
                schema_version VARCHAR NOT NULL,
                id VARCHAR PRIMARY KEY,
                type VARCHAR NOT NULL,
                source_id VARCHAR NOT NULL,
                target_id VARCHAR NOT NULL,
                weight REAL NOT NULL DEFAULT 1.0,
                attributes JSON DEFAULT '{}',
                created_at VARCHAR NOT NULL,
                valid_from VARCHAR NOT NULL,
                valid_to VARCHAR,
                deprecated BOOLEAN DEFAULT false
            );
        """,
        "entity_resolution": """
            CREATE TABLE IF NOT EXISTS entity_resolution (
                schema_version VARCHAR NOT NULL,
                id VARCHAR PRIMARY KEY,
                candidate_name VARCHAR NOT NULL,
                resolved_node_id VARCHAR NOT NULL,
                source_event_id VARCHAR DEFAULT '',
                method VARCHAR DEFAULT 'string_similarity',
                resolved_at VARCHAR NOT NULL
            );
        """,
        "attribute_change": """
            CREATE TABLE IF NOT EXISTS attribute_change (
                schema_version VARCHAR NOT NULL,
                id VARCHAR PRIMARY KEY,
                entity_type VARCHAR NOT NULL,
                entity_id VARCHAR NOT NULL,
                attribute VARCHAR NOT NULL,
                old_value VARCHAR,
                new_value VARCHAR,
                changed_at VARCHAR NOT NULL,
                reason VARCHAR DEFAULT ''
            );
        """,
    }

    def __init__(
        self,
        db_path: str,
        validator: SchemaValidator | None = None,
        migration_engine: MigrationEngine | None = None,
    ) -> None:
        self._db_path = db_path
        self._validator = validator or SchemaValidator()
        self._migration_engine = migration_engine or MigrationEngine()
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = duckdb.connect(db_path)
        self._init_schemas()

    def _init_schemas(self) -> None:
        for ddl in self.SCHEMAS.values():
            self._conn.execute(ddl)

    def get(self, record_type: str, id: str) -> dict[str, Any] | None:
        table = record_type
        if table not in self.SCHEMAS:
            return None
        result = self._conn.execute(f'SELECT * FROM "{table}" WHERE id = ?', [id]).fetchone()
        if result is None:
            return None
        cols = [desc[0] for desc in self._conn.description]
        record = dict(zip(cols, self._parse_row(result)))
        return self._migration_engine.migrate_if_needed(record, "0.1.0")

    def query(self, record_type: str, spec: dict[str, Any]) -> list[dict[str, Any]]:
        table = record_type
        if table not in self.SCHEMAS:
            return []
        conditions: list[str] = []
        params: list[Any] = []
        order_col = "timestamp DESC"
        for key, value in spec.items():
            if key in ("limit", "offset", "order_by"):
                if key == "order_by":
                    order_map = {
                        "priority": "priority ASC",
                        "timestamp": "timestamp DESC",
                        "queued_at": "queued_at ASC",
                        "persona_snapshot": """
            CREATE TABLE IF NOT EXISTS persona_snapshot (
                schema_version VARCHAR NOT NULL,
                id VARCHAR PRIMARY KEY,
                model_id VARCHAR NOT NULL,
                vector JSON NOT NULL,
                timestamp VARCHAR NOT NULL,
                reason VARCHAR DEFAULT ''
            );
        """,
                    }
                    order_col = order_map.get(str(value), "timestamp DESC")
                continue
            if key == "time_start":
                conditions.append("timestamp >= ?")
                params.append(value)
            elif key == "time_end":
                conditions.append("timestamp <= ?")
                params.append(value)
            elif key == "tags" and isinstance(value, list):
                conditions.append(" OR ".join("tags::VARCHAR LIKE ?" for _ in value))
                params.extend(f"%{t}%" for t in value)
            else:
                conditions.append(f'"{key}" = ?')
                params.append(value)
        where = " AND ".join(conditions) if conditions else "TRUE"
        limit = spec.get("limit", 100)
        offset = spec.get("offset", 0)
        result = self._conn.execute(
            f'SELECT * FROM "{table}" WHERE {where} ORDER BY {order_col} LIMIT ? OFFSET ?',
            params + [limit, offset],
        ).fetchall()
        cols = [desc[0] for desc in self._conn.description]
        return [
            self._migration_engine.migrate_if_needed(dict(zip(cols, self._parse_row(row))), "0.1.0")
            for row in result
        ]

    def insert(self, record_type: str, record: dict[str, Any]) -> str:
        if record_type not in self.SCHEMAS:
            raise ValueError(f"Unknown record type: {record_type}")
        self._validator.validate(record_type, record)
        table = record_type
        cols = list(record.keys())
        placeholders = ["?" for _ in cols]
        values = [self._serialize(v) for v in record.values()]
        self._conn.execute(
            f'INSERT INTO "{table}" ({", ".join(f'"{c}"' for c in cols)}) '
            f"VALUES ({', '.join(placeholders)})",
            values,
        )
        return str(record["id"])

    def update(self, record_type: str, id: str, changes: dict[str, Any]) -> bool:
        table = record_type
        if table not in self.SCHEMAS:
            return False
        existing = self.get(record_type, id)
        if existing is None:
            return False
        set_clause = ", ".join(f'"{k}" = ?' for k in changes)
        values = [self._serialize(v) for v in changes.values()] + [id]
        self._conn.execute(f'UPDATE "{table}" SET {set_clause} WHERE id = ?', values)
        return True

    def delete(self, record_type: str, id: str) -> bool:
        table = record_type
        if table not in self.SCHEMAS:
            return False
        self._conn.execute(f'DELETE FROM "{table}" WHERE id = ?', [id])
        return True

    def count(self, record_type: str, filter: dict[str, Any] | None = None) -> int:
        table = record_type
        if table not in self.SCHEMAS:
            return 0
        if filter:
            conditions = [f'"{k}" = ?' for k in filter]
            params = list(filter.values())
            result = self._conn.execute(
                f'SELECT COUNT(*) FROM "{table}" WHERE {" AND ".join(conditions)}',
                params,
            ).fetchone()
        else:
            result = self._conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()
        return int(result[0]) if result else 0

    def close(self) -> None:
        self._conn.close()

    def execute_raw(self, sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        result = self._conn.execute(sql, params or []).fetchall()
        cols = [desc[0] for desc in self._conn.description] if self._conn.description else []
        return [dict(zip(cols, self._parse_row(row))) for row in result]

    @staticmethod
    def _serialize(v: Any) -> Any:
        if isinstance(v, (dict, list)):
            return json.dumps(v, default=str)
        return v

    @staticmethod
    def _parse_row(row: tuple[Any, ...]) -> list[Any]:
        parsed = []
        for v in row:
            if isinstance(v, str):
                try:
                    parsed.append(json.loads(v))
                except (json.JSONDecodeError, ValueError):
                    parsed.append(v)
            else:
                parsed.append(v)
        return parsed
