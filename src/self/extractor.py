"""Extractor — transforms observation events into knowledge objects."""

from __future__ import annotations

import logging
from typing import Any

from self.event_batcher import EventBatcher
from self.knowledge_writer import KnowledgeWriter
from self.model_client import ModelClient
from self.output_validator import OutputValidator
from self.prompt_library import format_prompt, list_prompts


class Extractor:
    def __init__(
        self,
        model_client: ModelClient,
        knowledge_writer: KnowledgeWriter,
        batcher: EventBatcher | None = None,
        validator: OutputValidator | None = None,
        identity_graph: Any | None = None,
    ) -> None:
        self._model = model_client
        self._writer = knowledge_writer
        self._batcher = batcher or EventBatcher()
        self._validator = validator or OutputValidator()
        self._identity_graph = identity_graph
        self._log = logging.getLogger("self.extractor")

    def process_events(
        self,
        events: list[dict[str, Any]],
        prompt_ids: list[str] | None = None,
    ) -> list[str]:
        prompts = prompt_ids or list_prompts()
        batches = self._batcher.source_batches(events)
        produced_ids: list[str] = []

        for batch in batches:
            for prompt_id in prompts:
                try:
                    ids = self._extract_batch(batch, prompt_id)
                    produced_ids.extend(ids)
                except Exception:
                    self._log.exception(
                        "Extraction failed for prompt %s on batch of %d events",
                        prompt_id,
                        len(batch),
                    )
        return produced_ids

    def _extract_batch(
        self,
        events: list[dict[str, Any]],
        prompt_id: str,
    ) -> list[str]:
        event_text = self._batcher.format_events(events)
        system, user = format_prompt(prompt_id, event_text)
        response = self._model.generate(prompt=user, system=system)

        raw_text = response.get("text", "")
        if not raw_text.strip():
            self._log.warning("Empty response from model for prompt %s", prompt_id)
            return []

        parsed = self._validator.parse_json(raw_text)
        prompt_def = self._get_prompt_def(prompt_id)
        validated = self._validator.validate_schema(parsed, prompt_def["output_schema"])

        source_ids = [e.get("id", "") for e in events if e.get("id")]
        produced_ids: list[str] = []
        for item in validated:
            name = item.get("content", item.get("name", "unknown"))[:256]
            description = item.get("description", item.get("content", ""))
            confidence = item.get("confidence", 0.5)
            ko_type = prompt_id.replace("extract_", "").replace("detect_", "")

            # Resolve entities using Identity Graph if available
            entity_id = None
            if self._identity_graph:
                entity_id = self._resolve_entity_from_item(item, ko_type)

            ko_id = self._writer.write(
                type=ko_type,
                name=name,
                description=description,
                content=item.get("content", ""),
                confidence=confidence,
                source_event_ids=source_ids,
                prompt_id=prompt_id,
                model_id=self._model.model_name,
                reasoning=f"Extracted via {prompt_id} from {len(events)} events",
                entity_id=entity_id,
            )
            produced_ids.append(ko_id)
        return produced_ids

    def _resolve_entity_from_item(self, item: dict[str, Any], ko_type: str) -> str | None:
        if not self._identity_graph:
            return None

        entity_name = item.get("entity", item.get("name", ""))
        if not entity_name:
            return None

        node_type = "person" if ko_type in ["belief", "goal", "project"] else "concept"
        existing = self._identity_graph.resolver.resolve(entity_name)
        if existing:
            return existing.id

        node_id = self._identity_graph.node_store.create(node_type, entity_name)
        return node_id

    def _get_prompt_def(self, prompt_id: str) -> dict[str, Any]:
        from self.prompt_library import get_prompt as gp

        return gp(prompt_id)
