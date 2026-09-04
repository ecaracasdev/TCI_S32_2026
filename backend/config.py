"""Declarative application configuration definition."""

from __future__ import annotations

import logging
from pathlib import Path

from autoconfig import ConfigurationDefinition, ConfigurationSection, config_field
from typing import ClassVar


class Logs(ConfigurationSection):
    """Logging configuration."""

    LOGS_LEVEL: int = config_field(logging.INFO)
    LOGS_FILE: str = config_field("app.log")
    LOGS_DIR: str = config_field("logs")
    LOGS_FORMAT: str = config_field("[%(levelname)s] -> [%(asctime)s]: %(message)s")
    LOGS_DATE_FORMAT: str = config_field("%Y-%m-%d %H:%M")
    LOGS_DISABLE: bool = config_field(False)


class Database(ConfigurationSection):
    """Database connection configuration."""

    DB_TYPE: str = config_field("sqlite3")
    DB_HOST: str = config_field("localhost")
    DB_PORT: int = config_field(8000)
    DB_DRIVER: str = config_field("")
    DB_NAME: str = config_field("db")
    DB_USER: str = config_field("db_user")
    DB_PASSWORD: str = config_field("123456", secret=True)

    @property
    def url(self) -> str:
        db_type = self.DB_TYPE.lower()
        is_sqlite_type = db_type in ("sqlite", "sqlite3")

        if is_sqlite_type:
            driver = f"+{self.DB_DRIVER}" if self.DB_DRIVER else "+aiosqlite"
            if self.DB_NAME == ":memory:":
                return f"sqlite{driver}:///:memory:"
            return f"sqlite{driver}:///{self.DB_NAME}"

        driver = f"+{self.DB_DRIVER}" if self.DB_DRIVER else ""
        return (
            f"{db_type}{driver}://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )


class Secrets(ConfigurationSection):
    """Application secrets."""

    SECRET_KEY: str = config_field(secret=True)


class AuthOAuth(ConfigurationSection):
    """Generic OAuth configuration."""

    ENABLED: bool = config_field(False)
    PROVIDER: str = config_field("generic")
    CLIENT_ID: str = config_field("")
    CLIENT_SECRET: str = config_field("", secret=True)
    AUTHORIZE_URL: str = config_field("")
    TOKEN_URL: str = config_field("")
    USERINFO_URL: str = config_field("")
    REDIRECT_URI: str = config_field("http://localhost:5002/auth/oauth/callback")
    SCOPES: list[str] = config_field(default_factory=lambda: ["openid", "email", "profile"])
    USE_PKCE: bool = config_field(True)


class AuthKeycloak(ConfigurationSection):
    """Bearer-token authentication configuration for Keycloak."""

    ENABLED: bool = config_field(False)
    URL: str = config_field("http://localhost:8080")
    REALM: str = config_field("master")
    CLIENT_ID: str = config_field("")
    CLIENT_SECRET: str = config_field("", secret=True)
    VERIFY: bool = config_field(True)
    AUTHENTICATION_SCHEME: str = config_field("Bearer")
    VALIDATE_TOKEN: bool = config_field(True)
    REJECT_ON_MISSING_CLAIM: bool = config_field(False)
    CLAIMS: list[str] = config_field(
        default_factory=lambda: [
            "sub",
            "name",
            "family_name",
            "given_name",
            "preferred_username",
            "email",
            "email_verified",
            "iss",
            "aud",
            "azp",
            "realm_access",
            "resource_access",
            "groups",
            "scope",
            "permissions",
        ]
    )
    EXCLUDE_PATTERNS: list[str] = config_field(
        default_factory=lambda: [
            r"^/$",
            r"^/health$",
            r"^/docs$",
            r"^/openapi.json$",
            r"^/redoc$",
        ]
    )
    ADD_SWAGGER_AUTH: bool = config_field(False)
    SWAGGER_CLIENT_ID: str = config_field("")


class Auth(ConfigurationSection):
    """Authentication configuration."""

    ENABLED: bool = config_field(True)
    TOKEN_TTL_MINUTES: int = config_field(60 * 24)
    TOKEN_SALT: str = config_field("auth-token", secret=True)
    SESSION_COOKIE_NAME: str = config_field("session")
    SESSION_MAX_AGE_SECONDS: int = config_field(60 * 60 * 24)
    SESSION_SAME_SITE: str = config_field("lax")
    SESSION_HTTPS_ONLY: bool = config_field(False)
    OAUTH: AuthOAuth = config_field(default_factory=AuthOAuth)
    KEYCLOAK: AuthKeycloak = config_field(default_factory=AuthKeycloak)


class Server(ConfigurationSection):
    """HTTP server configuration."""

    HOST: str = config_field("localhost")
    PORT: int = config_field(5002)
    DEBUG: bool = config_field(False)
    VERSION: str = config_field("1.0.0")
    CORS_URLS: list[str] = config_field(default_factory=lambda: ["http://localhost"])
    RESTRICTED_MODULES: list[str] = config_field(default_factory=list)


class Config(ConfigurationDefinition):
    """Complete application configuration loaded from TOML or another supported format."""

    # Runtime-only metadata retained for compatibility with the existing app.
    NAME: ClassVar[str] = "default"
    CONFIG_FILE: ClassVar[Path] = Path(__file__).parent / "config.toml"

    server: Server = config_field()
    secrets: Secrets = config_field()
    database: Database = config_field()
    logs: Logs = config_field()
    auth: Auth = config_field(default_factory=Auth)
