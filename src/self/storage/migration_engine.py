"""Schema migration engine for SELF."""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable
from typing import Any

MigrationFunc = Callable[[dict[str, Any], str, str], dict[str, Any]]


class MigrationEngine:
    def __init__(self) -> None:
        self._migrations: dict[str, list[MigrationFunc]] = {}

    def register_migration(self, record_type: str, migration: MigrationFunc) -> None:
        self._migrations.setdefault(record_type, []).append(migration)

    def load_migrations(self) -> None:
        try:
            import tools.schema_migrate as pkg

            for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
                if modname.startswith("migrate_"):
                    module = importlib.import_module(f"tools.schema_migrate.{modname}")
                    if hasattr(module, "migrate"):
                        parts = modname.split("_", 2)
                        if len(parts) >= 2:
                            record_type = parts[1]
                            self.register_migration(record_type, module.migrate)
        except ImportError:
            pass

    def migrate(self, record: dict[str, Any], from_version: str, to_version: str) -> dict[str, Any]:
        record_type = record.get("type", "unknown")
        migrations = self._migrations.get(record_type, [])
        result = dict(record)
        for m in migrations:
            result = m(result, from_version, to_version)
        return result

    def migrate_if_needed(self, record: dict[str, Any], current_version: str) -> dict[str, Any]:
        record_version = record.get("schema_version", "0.0.0")
        if record_version != current_version:
            return self.migrate(record, record_version, current_version)
        return record
