"""Provenance Linker — links summaries to source records."""

from __future__ import annotations

from typing import Any


class ProvenanceLinker:
    def link(self, summary_id: str, context: dict[str, Any]) -> dict[str, Any]:
        source_ids: dict[str, list[str]] = {"events": [], "knowledge": [], "nodes": []}
        for e in context.get("events", []):
            eid = e.get("id") or e.get("event_id", "")
            if eid:
                source_ids["events"].append(eid)
        for k in context.get("knowledge", []):
            kid = k.get("id", "")
            if kid:
                source_ids["knowledge"].append(kid)
        for n in context.get("nodes", []):
            nid = n.get("id", "")
            if nid:
                source_ids["nodes"].append(nid)
        return {
            "summary_id": summary_id,
            "source_records": source_ids,
            "total_sources": sum(len(v) for v in source_ids.values()),
            "synthesis_params": {},
        }
