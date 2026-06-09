"""Schema Registry — versioned node/edge type definitions."""

from __future__ import annotations

from typing import Any

NODE_TYPES: dict[str, dict[str, Any]] = {
    "user": {"description": "The user themselves", "singleton": True},
    "person": {"description": "Another human the user interacts with"},
    "project": {"description": "A project the user is working on"},
    "organization": {"description": "A company, group, or institution"},
    "tool": {"description": "A software tool, library, or service"},
    "concept": {"description": "An idea, topic, or field of knowledge"},
    "place": {"description": "A physical or virtual location"},
    "event": {"description": "A significant occurrence"},
    "artifact": {"description": "A file, document, or created work"},
    "goal": {"description": "A goal the user is pursuing"},
    "interest": {"description": "An interest the user has"},
    "belief": {"description": "A belief the user holds"},
    "community": {"description": "A group or community"},
    "publication": {"description": "A published work"},
}

EDGE_TYPES: dict[str, dict[str, Any]] = {
    "knows": {"description": "Person-Person relationship", "directed": False},
    "works_on": {"description": "Person-Project, Person-Organization", "directed": True},
    "member_of": {"description": "Person-Organization", "directed": True},
    "part_of": {"description": "Project-Project, Project-Organization", "directed": True},
    "uses": {"description": "Person-Tool", "directed": True},
    "related_to": {"description": "Concept-Concept", "directed": False},
    "located_in": {"description": "Person/Organization-Place", "directed": True},
    "participated_in": {"description": "Person-Event", "directed": True},
    "created": {"description": "Person-Artifact", "directed": True},
    "believes": {"description": "Person-Belief", "directed": True},
    "pursues": {"description": "Person-Goal", "directed": True},
    "interested_in": {"description": "Person-Interest", "directed": True},
    "knows_about": {"description": "Person-Concept", "directed": True},
}


class SchemaRegistry:
    VERSION = "0.1.0"

    def is_valid_node_type(self, node_type: str) -> bool:
        return node_type in NODE_TYPES

    def is_valid_edge_type(self, edge_type: str) -> bool:
        return edge_type in EDGE_TYPES or edge_type.startswith("custom_")

    def is_valid_attribute(self, node_type: str, key: str) -> bool:
        return True

    def list_node_types(self) -> list[str]:
        return list(NODE_TYPES.keys())

    def list_edge_types(self) -> list[str]:
        return list(EDGE_TYPES.keys())

    def register_node_type(self, name: str, **attrs: Any) -> None:
        if name not in NODE_TYPES:
            NODE_TYPES[name] = attrs

    def register_edge_type(self, name: str, **attrs: Any) -> None:
        if name not in EDGE_TYPES:
            EDGE_TYPES[name] = attrs
