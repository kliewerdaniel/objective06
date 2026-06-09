"""Action Engine — effector subsystem for SELF."""

from __future__ import annotations

from .action_engine import ActionEngine
from .capability_registry import CapabilityRegistry
from .confirmation_manager import ConfirmationManager
from .executor import Executor
from .permission_resolver import PermissionResolver
from .plan_synthesizer import PlanSynthesizer
from .rollback_engine import RollbackEngine

__all__ = [
    "ActionEngine",
    "CapabilityRegistry",
    "PermissionResolver",
    "PlanSynthesizer",
    "Executor",
    "RollbackEngine",
    "ConfirmationManager",
]
