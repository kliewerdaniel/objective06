"""Security facade — authentication, authorization, secrets, injection defense."""

from __future__ import annotations

from typing import Any

from .auth_manager import AuthManager
from .authorization_engine import AuthorizationEngine
from .injection_classifier import InjectionClassifier
from .secret_manager import SecretManager


class Security:
    def __init__(self, storage: Any) -> None:
        self._storage = storage
        self.auth = AuthManager(storage)
        self.authorization = AuthorizationEngine(storage)
        self.secrets = SecretManager(storage)
        self.injection = InjectionClassifier()

    def login(self, user: str, key: str) -> dict[str, Any]:
        return self.auth.authenticate(user, key)

    def validate_session(self, token: str) -> dict[str, Any]:
        return self.auth.validate(token)

    def check_permission(self, user: str, capability: str) -> dict[str, Any]:
        return self.authorization.check(user, capability)

    def grant_permission(
        self, user: str, capability: str, scope: str = "*", ttl_hours: int = 0
    ) -> str:
        return self.authorization.grant(user, capability, scope, ttl_hours)

    def classify_input(self, text: str) -> dict[str, Any]:
        return self.injection.score(text)
