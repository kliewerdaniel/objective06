"""Main entry point for SELF — wires all 11 subsystems together."""

from __future__ import annotations

import logging
import signal
import sys
import time
from typing import Any

from self.action_engine import ActionEngine
from self.audit_log import AuditLog
from self.config import Config
from self.digital_twin import DigitalTwin
from self.evaluation import Evaluation
from self.event_batcher import EventBatcher
from self.event_log import EventLog
from self.extractor import Extractor
from self.health import HealthMonitor, SubsystemStatus
from self.identity_graph import IdentityGraph
from self.ingest_queue import IngestQueue
from self.knowledge_writer import KnowledgeWriter
from self.memory import MemoryAPI
from self.metrics import get_collector
from self.model_client import ModelClient
from self.normalizer import Normalizer
from self.observer import Observer
from self.onboarding import OnboardingFlow
from self.orchestrator import Orchestrator
from self.output_validator import OutputValidator
from self.persona_engine import PersonaEngine
from self.security import Security
from self.source_adapters import FilesystemWatcher, GitPollingAdapter
from self.storage import DuckDBAdapter, FAISSAdapter, MigrationEngine, SchemaValidator
from self.synthesis_engine import SynthesisEngine


def main() -> None:
    config = Config.from_env()
    config.ensure_dirs()

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )
    log = logging.getLogger("self.main")

    metrics = get_collector()
    health = HealthMonitor(heartbeat_timeout=30.0)

    log.info("SELF v0.1.0 starting — all 11 subsystems")
    metrics.increment("system.startup")

    # ── Phase 1: Foundation ──────────────────────────────────────────
    validator = SchemaValidator()
    migration_engine = MigrationEngine()
    migration_engine.load_migrations()

    storage = DuckDBAdapter(
        db_path=config.duckdb_path,
        validator=validator,
        migration_engine=migration_engine,
    )
    health.heartbeat("storage")
    log.info("Storage initialized (%s)", config.duckdb_path)
    metrics.increment("system.storage.init")

    audit_log = AuditLog(storage=storage, audit_head_path=config.audit_head_path)
    health.heartbeat("audit_log")
    log.info("Audit log initialized")

    event_log = EventLog(storage=storage, raw_dir=config.raw_dir)
    log.info("Event log initialized")

    audit_log.append("system", "start", "system", "self", reason="SELF startup")

    needs_onboarding = OnboardingFlow.needs_onboarding(storage)
    if needs_onboarding:
        log.warning("No onboarding found — run onboarding flow first")
    else:
        log.info("Onboarding already completed")

    faiss = FAISSAdapter(index_path=config.faiss_index_path, dimension=768)
    log.info("Vector index initialized (%s)", config.faiss_index_path)

    # ── Phase 2: Observation ─────────────────────────────────────────
    normalizer = Normalizer(producer="observer")
    ingest_queue = IngestQueue(storage)
    health.heartbeat("ingest_queue")

    observer = Observer(
        normalizer=normalizer,
        ingest_queue=ingest_queue,
        event_log=event_log,
        health_monitor=health,
        metrics=metrics,
        adapters=[],
    )
    log.info("Observer initialized")

    if config.watch_paths:
        fs_watcher = FilesystemWatcher(config.watch_paths)
        observer.register_adapter(fs_watcher)
        log.info("Filesystem watcher registered for %s", config.watch_paths)

    if config.watch_repos:
        git_adapter = GitPollingAdapter(config.watch_repos)
        observer.register_adapter(git_adapter)
        log.info("Git poller registered for %s", config.watch_repos)

    # ── Phase 3: Extraction ──────────────────────────────────────────
    extraction_model = ModelClient(
        model=config.embedding_model,
        timeout=60.0,
        max_retries=3,
    )
    event_batcher = EventBatcher()
    output_validator = OutputValidator()
    knowledge_writer = KnowledgeWriter(
        storage=storage,
        audit_log=audit_log,
    )
    extractor = Extractor(
        model_client=extraction_model,
        knowledge_writer=knowledge_writer,
        batcher=event_batcher,
        validator=output_validator,
    )
    log.info("Extractor initialized (model=%s)", config.embedding_model)

    # ── Phase 4: Memory ──────────────────────────────────────────────
    memory = MemoryAPI(
        storage=storage,
        audit_log=audit_log,
        event_log=event_log,
        faiss_adapter=faiss,
    )
    log.info("Memory initialized")

    # ── Phase 5: Identity Graph ──────────────────────────────────────
    identity_graph = IdentityGraph(storage=storage, audit_log=audit_log)
    log.info("Identity graph initialized")

    # ── Phase 6: Persona Engine ──────────────────────────────────────
    persona_model = ModelClient(
        model=config.embedding_model,
        timeout=30.0,
        max_retries=2,
    )
    persona_engine = PersonaEngine(
        storage=storage,
        model_client=persona_model,
        vector_dir=config.vector_dir,
    )
    log.info("Persona engine initialized (model=%s)", config.embedding_model)

    # ── Phase 7: Digital Twin ────────────────────────────────────────
    twin_model = ModelClient(
        model=config.embedding_model,
        timeout=120.0,
        max_retries=3,
    )
    digital_twin = DigitalTwin(
        memory=memory,
        model_client=twin_model,
        identity_graph=identity_graph,
        persona_engine=persona_engine,
    )
    log.info("Digital twin initialized")

    # ── Phase 8: Action Engine ───────────────────────────────────────
    action_engine = ActionEngine(storage=storage)
    log.info("Action engine initialized")

    # ── Phase 9: Synthesis Engine ────────────────────────────────────
    synthesis_model = ModelClient(
        model=config.embedding_model,
        timeout=120.0,
        max_retries=3,
    )
    synthesis_engine = SynthesisEngine(
        memory=memory,
        model_client=synthesis_model,
        identity_graph=identity_graph,
        storage=storage,
    )
    log.info("Synthesis engine initialized")

    # ── Phase 11: Security ──────────────────────────────────────────
    security = Security(storage=storage)
    log.info("Security initialized")

    # ── Evaluation (cross-cutting) ────────────────────────────────────
    evaluation = Evaluation(storage=storage)
    evaluation.register_builtins()

    def _eval_extraction(inputs: dict[str, Any]) -> dict[str, Any]:
        events = inputs.get("events", [])
        prompt_ids = inputs.get("prompt_ids", None)
        try:
            ids = extractor.process_events(events, prompt_ids)
            return {"ids": ids, "count": len(ids)}
        except Exception as exc:
            return {"ids": [], "count": 0, "error": str(exc)}

    def _eval_memory(inputs: dict[str, Any]) -> dict[str, Any]:
        query_vec = inputs.get("vector", [])
        k = inputs.get("k", 10)
        try:
            results = memory.semantic_search(query_vec, k)
            return {"results": results, "count": len(results)}
        except Exception as exc:
            return {"results": [], "count": 0, "error": str(exc)}

    def _eval_identity_graph(inputs: dict[str, Any]) -> dict[str, Any]:
        name = inputs.get("name", "")
        try:
            resolved = identity_graph.resolver.resolve(name)
            return {"resolved": resolved, "found": resolved is not None}
        except Exception as exc:
            return {"resolved": None, "found": False, "error": str(exc)}

    def _eval_persona(inputs: dict[str, Any]) -> dict[str, Any]:
        knowledge = inputs.get("knowledge", {})
        try:
            score = persona_engine.consistency(knowledge)
            return {"score": score, "consistency": score}
        except Exception as exc:
            return {"score": 0.0, "consistency": 0.0, "error": str(exc)}

    evaluation.register_handler("extraction", _eval_extraction)
    evaluation.register_handler("memory", _eval_memory)
    evaluation.register_handler("identity_graph", _eval_identity_graph)
    evaluation.register_handler("persona_engine", _eval_persona)
    log.info("Evaluation subsystem initialized with real handlers")

    # ── Phase 10: Orchestrator ───────────────────────────────────────
    _subsystems = {
        "identity_graph": identity_graph,
        "persona_engine": persona_engine,
        "digital_twin": digital_twin,
        "action_engine": action_engine,
        "synthesis_engine": synthesis_engine,
        "security": security,
        "evaluation": evaluation,
    }
    orchestrator = Orchestrator(
        observer=observer,
        extractor=extractor,
        memory=memory,
        health=health,
        audit_log=audit_log,
        loop_interval=config.loop_interval_ms / 1000.0,
    )
    health.heartbeat("orchestrator", SubsystemStatus.HEALTHY, "all subsystems online")
    metrics.gauge("system.subsystems", 12)
    log.info("Orchestrator initialized — all subsystems online")

    # ── Main Loop ────────────────────────────────────────────────────
    shutdown_requested = False

    def _handle_signal(signum: int, frame: object) -> None:
        nonlocal shutdown_requested
        log.info("Signal %d received — shutting down...", signum)
        shutdown_requested = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    orchestrator.start()
    log.info("SELF running. Press Ctrl+C to stop.")

    loop_interval = config.loop_interval_ms / 1000.0
    try:
        while not shutdown_requested:
            orchestrator.tick()
            time.sleep(loop_interval)
    except KeyboardInterrupt:
        log.info("Keyboard interrupt received")
    finally:
        log.info("Initiating graceful shutdown...")
        orchestrator.stop()
        faiss.close()
        audit_log.append("system", "stop", "system", "self", reason="SELF shutdown")
        metrics.increment("system.shutdown")
        metrics.gauge("system.uptime_seconds", time.time())
        storage.close()
        log.info("SELF shutdown complete. Goodbye.")


if __name__ == "__main__":
    main()
