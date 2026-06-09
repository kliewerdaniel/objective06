"""Capability Registry — authoritative list of SELF capabilities."""

from __future__ import annotations

from typing import Any

CAPABILITY_DEFINITIONS: dict[str, dict[str, Any]] = {
    "read_file": {
        "id": "read_file",
        "description": "Read the contents of a file at the given path.",
        "required_permission": "fs:read",
        "sensitivity": "safe",
        "params": {
            "path": {"type": "string", "description": "Absolute path to the file to read"},
        },
        "example": {"path": "/tmp/example.txt"},
    },
    "list_directory": {
        "id": "list_directory",
        "description": "List files and directories at the given path.",
        "required_permission": "fs:read",
        "sensitivity": "safe",
        "params": {
            "path": {"type": "string", "description": "Absolute directory path"},
        },
        "example": {"path": "/tmp"},
    },
    "write_file": {
        "id": "write_file",
        "description": "Write content to a file at the given path.",
        "required_permission": "fs:write",
        "sensitivity": "sensitive",
        "params": {
            "path": {"type": "string", "description": "Absolute path to write to"},
            "content": {"type": "string", "description": "Content to write to the file"},
        },
        "example": {"path": "/tmp/example.txt", "content": "hello world"},
    },
}


class CapabilityRegistry:
    def get(self, capability_id: str) -> dict[str, Any] | None:
        return CAPABILITY_DEFINITIONS.get(capability_id)

    def list_all(self) -> list[dict[str, Any]]:
        return list(CAPABILITY_DEFINITIONS.values())

    def has(self, capability_id: str) -> bool:
        return capability_id in CAPABILITY_DEFINITIONS
