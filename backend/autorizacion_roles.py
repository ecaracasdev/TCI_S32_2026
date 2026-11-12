"""Dependencias FastAPI para consultar usuarios y aplicar RBAC."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from autenticacion_jwt import TokenInvalidoError, validar_token_jwt
from config import Config
from db.database import get_db
from db.db_models.usuario_db import UsuarioDb
from utils import get_config


TipoCoincidencia = Literal["alguno", "todos"]
ATRIBUTOS_USUARIO_CONSULTABLES = frozenset(
    {"id", "nombre", "apellido", "genero", "correo", "verificado"}
)


def usuario_tiene_rol(usuario: UsuarioDb | None, rol: str) -> bool:
    """Indica si el usuario tiene el rol indicado."""

    return usuario is not None and any(
        rol_asignado.nombre == rol for rol_asignado in usuario.roles
    )


def usuario_tiene_algun_rol(usuario: UsuarioDb | None, *roles: str) -> bool:
    """Indica si el usuario tiene al menos uno de los roles indicados."""

    return usuario is not None and any(usuario_tiene_rol(usuario, rol) for rol in roles)


def usuario_tiene_todos_los_roles(usuario: UsuarioDb | None, *roles: str) -> bool:
    """Indica si el usuario tiene todos los roles indicados."""

    return usuario is not None and bool(roles) and all(
        usuario_tiene_rol(usuario, rol) for rol in roles
    )


def usuario_tiene_atributo(
    usuario: UsuarioDb | None,
    atributo: str,
    valor: Any,
) -> bool:
    """Compara un atributo público del usuario con un valor esperado."""

    if usuario is None or atributo not in ATRIBUTOS_USUARIO_CONSULTABLES:
        return False
    return getattr(usuario, atributo, None) == valor


async def obtener_usuario_actual_opcional(
    request: Request,
    sesion: AsyncSession = Depends(get_db),
) -> UsuarioDb | None:
    """Devuelve el usuario autenticado o ``None`` si la ruta permite anonimato.

    Para una ruta opcional, agregar su patrón a ``auth.JWT.RUTAS_EXCLUIDAS``.
    Si se envía Bearer en esa ruta, el token se valida igualmente.
    """

    usuario_id = getattr(request.state, "usuario_id", None)
    if usuario_id is None:
        autorizacion = request.headers.get("Authorization", "")
        if not autorizacion:
            return None
        esquema, separador, token = autorizacion.partition(" ")
        if not separador or esquema.lower() != "bearer" or not token.strip():
            raise _no_autorizado("El encabezado de autenticación no es válido.")
        configuracion: Config = get_config()
        if not configuracion.auth.ENABLED or not configuracion.auth.JWT.HABILITADO:
            raise _no_autorizado("La autenticación JWT local no está habilitada.")
        try:
            claims = validar_token_jwt(configuracion, token.strip())
            usuario_id = int(claims["sub"])
        except (TokenInvalidoError, KeyError, TypeError, ValueError):
            raise _no_autorizado("El token Bearer no es válido.") from None

    resultado = await sesion.execute(
        select(UsuarioDb)
        .options(selectinload(UsuarioDb.roles))
        .where(UsuarioDb.id == usuario_id)
    )
    usuario = resultado.scalar_one_or_none()
    if usuario is None:
        raise _no_autorizado("El usuario del token ya no existe.")
    return usuario


async def obtener_usuario_actual(
    usuario: UsuarioDb | None = Depends(obtener_usuario_actual_opcional),
) -> UsuarioDb:
    if usuario is None:
        raise _no_autorizado("Se requiere autenticación.")
    return usuario


def _no_autorizado(detalle: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detalle,
        headers={"WWW-Authenticate": "Bearer"},
    )


def requiere_rol(
    *roles_requeridos: str,
    coincidencia: TipoCoincidencia = "alguno",
) -> Callable[..., UsuarioDb]:
    """Crea una dependencia que exige uno o varios roles persistidos."""

    if not roles_requeridos or any(not rol.strip() for rol in roles_requeridos):
        raise ValueError("requiere_rol necesita al menos un nombre de rol.")

    async def dependencia(
        usuario: UsuarioDb = Depends(obtener_usuario_actual),
    ) -> UsuarioDb:
        cumple = (
            usuario_tiene_todos_los_roles(usuario, *roles_requeridos)
            if coincidencia == "todos"
            else usuario_tiene_algun_rol(usuario, *roles_requeridos)
        )
        if not cumple:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no tiene el rol requerido.",
            )
        return usuario

    return dependencia


def requiere_atributo(atributo: str, valor: Any) -> Callable[..., UsuarioDb]:
    """Crea una dependencia que exige un valor concreto del usuario."""

    if atributo not in ATRIBUTOS_USUARIO_CONSULTABLES:
        raise ValueError(f"Atributo de usuario no autorizado: {atributo}")

    async def dependencia(
        usuario: UsuarioDb = Depends(obtener_usuario_actual),
    ) -> UsuarioDb:
        if not usuario_tiene_atributo(usuario, atributo, valor):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no cumple la condición requerida.",
            )
        return usuario

    return dependencia


__all__ = [
    "obtener_usuario_actual",
    "obtener_usuario_actual_opcional",
    "requiere_atributo",
    "requiere_rol",
    "usuario_tiene_algun_rol",
    "usuario_tiene_atributo",
    "usuario_tiene_rol",
    "usuario_tiene_todos_los_roles",
]
