from __future__ import annotations
from secrets import token_urlsafe
from time import time
from typing import Any
from urllib.parse import urlencode
from itsdangerous import URLSafeTimedSerializer

from config import Auth as AuthConfig
from services.base_service import Service
from utils import get_config


class AuthService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, "_auth_initialized", False):
            return

        cfg = get_config()
        self._config: AuthConfig = cfg.auth
        self._secret_key = cfg.secrets.SECRET_KEY
        self._token_serializer = URLSafeTimedSerializer(
            self._secret_key,
            salt=self._config.TOKEN_SALT,
        )
        self._oauth_state_serializer = URLSafeTimedSerializer(
            self._secret_key,
            salt=f"{self._config.TOKEN_SALT}:oauth-state",
        )
        self._auth_initialized = True

    @property
    def config(self) -> AuthConfig:
        return self._config

    def is_enabled(self) -> bool:
        return self._config.ENABLED

    def is_oauth_enabled(self) -> bool:
        oauth = self._config.OAUTH
        if not oauth.ENABLED:
            return False
        required_values = (
            oauth.CLIENT_ID,
            oauth.AUTHORIZE_URL,
            oauth.TOKEN_URL,
            oauth.USERINFO_URL,
            oauth.REDIRECT_URI,
        )
        if not all(required_values):
            return False
        if not oauth.USE_PKCE and not oauth.CLIENT_SECRET:
            return False
        return True

    def create_token(self, subject: str, claims: dict[str, Any] | None = None) -> str:
        payload: dict[str, Any] = {
            "sub": subject,
            "iat": int(time()),
            "ttl": self._config.TOKEN_TTL_MINUTES * 60,
        }
        if claims:
            payload["claims"] = claims
        return self._token_serializer.dumps(payload)

    def verify_token(self, token: str) -> dict[str, Any]:
        return self._token_serializer.loads(
            token,
            max_age=self._config.TOKEN_TTL_MINUTES * 60,
        )

    def create_oauth_state(self, payload: dict[str, Any] | None = None) -> str:
        data = {
            "nonce": token_urlsafe(24),
            "iat": int(time()),
        }
        if payload:
            data["payload"] = payload
        return self._oauth_state_serializer.dumps(data)

    def verify_oauth_state(self, state: str) -> dict[str, Any]:
        return self._oauth_state_serializer.loads(
            state,
            max_age=self._config.SESSION_MAX_AGE_SECONDS,
        )

    def build_oauth_authorize_url(
        self,
        state: str | None = None,
        redirect_uri: str | None = None,
        scopes: list[str] | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> tuple[str, str]:
        if not self.is_oauth_enabled():
            raise RuntimeError("OAuth is disabled or incomplete in the auth config")

        oauth = self._config.OAUTH
        current_state = state or self.create_oauth_state()
        query: dict[str, Any] = {
            "response_type": "code",
            "client_id": oauth.CLIENT_ID,
            "redirect_uri": redirect_uri or oauth.REDIRECT_URI,
            "scope": " ".join(scopes or oauth.SCOPES),
            "state": current_state,
        }
        if extra_params:
            query.update(extra_params)
        return f"{oauth.AUTHORIZE_URL}?{urlencode(query)}", current_state


