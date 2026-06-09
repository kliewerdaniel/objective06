"""Main entry point for SELF."""

from __future__ import annotations

import logging
import sys
import time


def main() -> None:
    from self.audit_log import AuditLog
    from self.config import Config
    from self.event_log import EventLog
    from self.health import HealthMonitor, SubsystemStatus
    from self.ingest_queue import IngestQueue
    from self.metrics import get_collector
    from self.normalizer import Normalizer
    from self.observer import Observer
    from self.onboarding import OnboardingFlow
    from self.source_adapters import FilesystemWatcher, GitPollingAdapter
    from self.storage import DuckDBAdapter, MigrationEngine, SchemaValidator

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

    log.info("SELF v0.1.0 starting...")

    validator = SchemaValidator()
    migration_engine = MigrationEngine()
    migration_engine.load_migrations()

    storage = DuckDBAdapter(
        db_path=config.duckdb_path,
        validator=validator,
        migration_engine=migration_engine,
    )
    health.heartbeat("storage")
    log.info("Storage initialized at %s", config.duckdb_path)
    metrics.increment("system.storage.init")

    audit_log = AuditLog(storage=storage, audit_head_path=config.audit_head_path)
    health.heartbeat("audit_log")
    log.info("Audit log initialized")

    event_log = EventLog(storage=storage, raw_dir=config.raw_dir)
    log.info("Event log initialized")

    audit_log.append("system", "start", "system", "self", reason="SELF startup")

    if OnboardingFlow.needs_onboarding(storage):
        log.warning("No onboarding found. Run onboarding flow first.")
    else:
        log.info("Onboarding already completed")

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

    health.heartbeat("main", SubsystemStatus.HEALTHY, "foundation initialized")
    metrics.increment("system.startup")

    log.info("SELF foundation initialized successfully")
    log.info("Foundation Complete")

    observer.start()
    loop_count = 0
    try:
        while True:
            time.sleep(config.loop_interval_ms / 1000.0)
            loop_count += 1
            observer.poll_once()
            if loop_count % 100 == 0:
                health.heartbeat("main")
                metrics.gauge("system.uptime_seconds", time.time())
                if not health.system_healthy:
                    log.warning("Degraded subsystems: %s", health.degraded_subsystems)
    except KeyboardInterrupt:
        log.info("Shutting down...")
        observer.stop()
        audit_log.append("system", "stop", "system", "self", reason="SELF shutdown")
        metrics.increment("system.shutdown")
        storage.close()
        log.info("Goodbye.")


if __name__ == "__main__":
    main()
