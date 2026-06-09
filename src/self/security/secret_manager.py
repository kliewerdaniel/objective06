"""Secret Manager — encrypted secret storage."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

_XOR_KEY = hashlib.sha256(b"self-secret-key-default").digest()


def _encrypt(value: str) -> str:
    data = value.encode()
    key = _XOR_KEY[: len(data)]
    encrypted = bytes(a ^ b for a, b in zip(data, key))
    return encrypted.hex()


def _decrypt(hex_value: str) -> str:
    encrypted = bytes.fromhex(hex_value)
    key = _XOR_KEY[: len(encrypted)]
    decrypted = bytes(a ^ b for a, b in zip(encrypted, key))
    return decrypted.decode()


class SecretManager:
    def __init__(self, storage: Any) -> None:
        self._storage = storage
        self._cache: dict[str, str] = {}

    def store(self, name: str, value: str) -> str:
        now = datetime.now(UTC)
        sid = f"sec_{uuid4().hex}"
        encrypted = _encrypt(value)
        record = {
            "schema_version": "0.1.0",
            "id": sid,
            "name": name,
            "encrypted_value": encrypted,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        self._storage.insert("secret_record", record)
        self._cache[name] = value
        return sid

    def retrieve(self, name: str) -> str | None:
        if name in self._cache:
            return self._cache[name]
        records = self._storage.query("secret_record", {"name": name, "limit": 1})
        if not records:
            return None
        encrypted = records[0].get("encrypted_value", "")
        value = _decrypt(encrypted)
        self._cache[name] = value
        return value

    def delete(self, name: str) -> bool:
        self._cache.pop(name, None)
        records = self._storage.query("secret_record", {"name": name, "limit": 1})
        if not records:
            return False
        rid = records[0]["id"]
        return self._storage.delete("secret_record", rid)

    def list_names(self) -> list[str]:
        records = self._storage.query("secret_record", {"limit": 1000})
        return [r["name"] for r in records]
