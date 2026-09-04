"""Authentication and authorization helpers for Keycloak-backed APIs.

The Keycloak middleware is responsible for validating the Bearer token. This
module normalizes the token claims into ``KeycloakUser`` and exposes small,
composable FastAPI dependencies for endpoint authorization.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any, Literal, TypeAlias
from urllib.parse import urlparse

from fastapi import Depends, HTTPException, status
from fastapi_keycloak_middleware import get_user as _get_middleware_user

from utils import get_config


MatchMode: TypeAlias = Literal["all", "any"]
RoleSource: TypeAlias = Literal["all", "realm", "client"]
UserMapper: TypeAlias = Callable[[Mapping[str, Any]], Awaitable["KeycloakUser"]]


def _as_list(value: Any) -> list[str]:
    """Return a string list from a Keycloak claim or an absent value."""

    if value is None:
        return []
    if isinstance(value, str):
        return [item for item in value.split() if item]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value if item is not None]
    return []


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _extract_realm(issuer: str, fallback: str = "") -> str:
    """Extract the realm segment from a Keycloak issuer URL."""

    path_parts = [part for part in urlparse(issuer).path.split("/") if part]
    try:
        return path_parts[path_parts.index("realms") + 1]
    except (ValueError, IndexError):
        return fallback


class KeycloakUser(dict[str, Any]):
    """Dictionary-compatible, normalized representation of a Keycloak user.

    The original claims remain available through normal dictionary operations,
    while commonly used values are normalized into stable keys and properties.
    """

    @classmethod
    def from_claims(
        cls,
        claims: Mapping[str, Any],
        *,
        client_id: str = "",
        keycloak_url: str = "",
        realm_name: str = "",
    ) -> "KeycloakUser":
        raw = dict(claims)
        realm_access = _as_mapping(raw.get("realm_access"))
        resource_access = _as_mapping(raw.get("resource_access"))

        realm_roles = _as_list(realm_access.get("roles"))
        client_roles_by_client = {
            str(name): _as_list(_as_mapping(value).get("roles"))
            for name, value in resource_access.items()
            if isinstance(value, Mapping)
        }
        client_roles = client_roles_by_client.get(client_id, [])
        all_client_roles = [
            role
            for roles in client_roles_by_client.values()
            for role in roles
        ]

        issuer = str(raw.get("iss") or "")
        realm = _extract_realm(issuer, realm_name)
        realm_url = issuer.rstrip("/")
        if not realm_url and keycloak_url and realm:
            realm_url = f"{keycloak_url.rstrip('/')}/realms/{realm}"

        permissions = _as_list(raw.get("permissions"))
        scopes = _as_list(raw.get("scope"))
        normalized = {
            **raw,
            "user_id": str(raw.get("sub") or ""),
            "username": str(
                raw.get("preferred_username")
                or raw.get("username")
                or ""
            ),
            "realm": realm,
            "realm_name": realm,
            "realm_url": realm_url,
            "issuer": issuer,
            "realm_roles": _unique(realm_roles),
            "client_roles": _unique(client_roles),
            "client_roles_by_client": {
                name: _unique(roles)
                for name, roles in client_roles_by_client.items()
            },
            "roles": _unique([*realm_roles, *all_client_roles]),
            "groups": _unique(_as_list(raw.get("groups"))),
            "permissions": _unique([*permissions, *scopes]),
            "client_id": client_id,
        }
        return cls(normalized)

    def __getattr__(self, name: str) -> Any:
        """Allow convenient attribute access to claims and normalized values."""

        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    @property
    def user_id(self) -> str:
        return str(self.get("user_id", ""))

    @property
    def username(self) -> str:
        return str(self.get("username", ""))

    @property
    def realm(self) -> str:
        return str(self.get("realm", ""))

    @property
    def realm_roles(self) -> list[str]:
        return list(self.get("realm_roles", []))

    @property
    def client_roles(self) -> list[str]:
        return list(self.get("client_roles", []))

    @property
    def client_roles_by_client(self) -> dict[str, list[str]]:
        return {
            name: list(roles)
            for name, roles in self.get("client_roles_by_client", {}).items()
        }

    @property
    def roles(self) -> list[str]:
        return list(self.get("roles", []))

    @property
    def groups(self) -> list[str]:
        return list(self.get("groups", []))

    @property
    def permissions(self) -> list[str]:
        return list(self.get("permissions", []))

    def has_role(self, role: str, *, source: RoleSource = "all") -> bool:
        roles = {
            "all": self.roles,
            "realm": self.realm_roles,
            "client": self.client_roles,
        }[source]
        return role in roles

    def has_group(self, group: str, *, include_children: bool = False) -> bool:
        if group in self.groups:
            return True
        if not include_children:
            return False
        prefix = group.rstrip("/") + "/"
        return any(item.startswith(prefix) for item in self.groups)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions or permission in self.roles


async def map_keycloak_user(claims: Mapping[str, Any]) -> KeycloakUser:
    """Map middleware claims into the application user object."""

    keycloak = get_config().auth.KEYCLOAK
    return KeycloakUser.from_claims(
        claims,
        client_id=keycloak.CLIENT_ID,
        keycloak_url=keycloak.URL,
        realm_name=keycloak.REALM,
    )


def get_current_user(
    user: KeycloakUser = Depends(_get_middleware_user),
) -> KeycloakUser:
    """Resolve the normalized authenticated user from the current request."""

    if isinstance(user, KeycloakUser):
        return user
    if isinstance(user, Mapping):
        return KeycloakUser.from_claims(user)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authenticated user is not available",
    )


def _matches(
    values: Sequence[str],
    required: Sequence[str],
    *,
    match: MatchMode,
) -> bool:
    if match == "any":
        return any(item in values for item in required)
    return all(item in values for item in required)


def _forbidden(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


def require_role(
    *required_roles: str,
    source: RoleSource = "all",
    match: MatchMode = "all",
) -> Callable[..., KeycloakUser]:
    """Create a dependency requiring one or more roles."""

    if not required_roles:
        raise ValueError("require_role needs at least one role")

    async def dependency(
        user: KeycloakUser = Depends(get_current_user),
    ) -> KeycloakUser:
        roles = {
            "all": user.roles,
            "realm": user.realm_roles,
            "client": user.client_roles,
        }[source]
        if not _matches(roles, required_roles, match=match):
            raise _forbidden("Required role is missing")
        return user

    return dependency


def require_realm_role(
    *required_roles: str,
    match: MatchMode = "all",
) -> Callable[..., KeycloakUser]:
    """Create a dependency requiring realm-level roles."""

    return require_role(*required_roles, source="realm", match=match)


def require_client_role(
    *required_roles: str,
    match: MatchMode = "all",
) -> Callable[..., KeycloakUser]:
    """Create a dependency requiring roles from the configured API client."""

    return require_role(*required_roles, source="client", match=match)


def require_group(
    group: str,
    *,
    include_children: bool = False,
) -> Callable[..., KeycloakUser]:
    """Create a dependency requiring membership in a Keycloak group."""

    async def dependency(
        user: KeycloakUser = Depends(get_current_user),
    ) -> KeycloakUser:
        if not user.has_group(group, include_children=include_children):
            raise _forbidden("Required group membership is missing")
        return user

    return dependency


def require_permission(
    *permissions: str,
    match: MatchMode = "all",
) -> Callable[..., KeycloakUser]:
    """Create a dependency requiring normalized permissions or matching roles."""

    if not permissions:
        raise ValueError("require_permission needs at least one permission")

    async def dependency(
        user: KeycloakUser = Depends(get_current_user),
    ) -> KeycloakUser:
        available = _unique([*user.permissions, *user.roles])
        if not _matches(available, permissions, match=match):
            raise _forbidden("Required permission is missing")
        return user

    return dependency


def username_equals(username: str) -> Callable[..., KeycloakUser]:
    """Create a dependency requiring an exact preferred username match."""

    async def dependency(
        user: KeycloakUser = Depends(get_current_user),
    ) -> KeycloakUser:
        if user.username != username:
            raise _forbidden("Username does not match")
        return user

    return dependency


require_username = username_equals


__all__ = [
    "KeycloakUser",
    "get_current_user",
    "map_keycloak_user",
    "require_client_role",
    "require_group",
    "require_permission",
    "require_realm_role",
    "require_role",
    "require_username",
    "username_equals",
]
