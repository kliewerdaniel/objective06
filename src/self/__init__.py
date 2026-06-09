"""SELF — Synthetic Evolutionary Local Framework."""

from __future__ import annotations

from .action_engine import ActionEngine
from .audit_log import AuditLog
from .compaction import CompactionEngine
from .config import Config
from .digital_twin import DigitalTwin
from .evaluation import EvalSpec, Evaluation
from .event_batcher import EventBatcher
from .event_log import EventLog
from .exporter import Exporter
from .extractor import Extractor
from .health import HealthMonitor, SubsystemStatus
from .identity_graph import IdentityGraph
from .ingest_queue import IngestQueue
from .knowledge_writer import KnowledgeWriter
from .memory import MemoryAPI
from .metrics import MetricsCollector, get_collector
from .model_client import ModelClient
from .normalizer import Normalizer
from .observer import Observer
from .onboarding import OnboardingFlow
from .orchestrator import Orchestrator
from .output_validator import OutputValidator
from .persona_engine import PersonaEngine
from .prompt_library import PROMPTS
from .retention import RetentionManager
from .schemas import AuditLogEntry, EventLogEntry, KnowledgeObject, ObservationEvent
from .security import Security
from .snapshot_manager import SnapshotManager
from .source_adapters import BaseSourceAdapter, FilesystemWatcher, GitPollingAdapter
from .storage import DuckDBAdapter, FAISSAdapter, MigrationEngine, SchemaValidator
from .synthesis_engine import SynthesisEngine

__all__ = [
    "Config",
    "ObservationEvent",
    "KnowledgeObject",
    "AuditLogEntry",
    "EventLogEntry",
    "AuditLog",
    "EventLog",
    "DuckDBAdapter",
    "FAISSAdapter",
    "SchemaValidator",
    "MigrationEngine",
    "OnboardingFlow",
    "MetricsCollector",
    "get_collector",
    "HealthMonitor",
    "SubsystemStatus",
    "Normalizer",
    "IngestQueue",
    "Observer",
    "BaseSourceAdapter",
    "FilesystemWatcher",
    "GitPollingAdapter",
    "EventBatcher",
    "Extractor",
    "KnowledgeWriter",
    "ModelClient",
    "OutputValidator",
    "PROMPTS",
    "MemoryAPI",
    "SnapshotManager",
    "CompactionEngine",
    "RetentionManager",
    "Exporter",
    "IdentityGraph",
    "PersonaEngine",
    "DigitalTwin",
    "Evaluation",
    "EvalSpec",
    "ActionEngine",
    "SynthesisEngine",
    "Orchestrator",
    "Security",
]

__version__ = "0.1.0"
