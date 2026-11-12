"""Casos de uso de usuarios, roles y credenciales."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from autenticacion_jwt import crear_hash_contrasena, verificar_contrasena
from db.db_models.rol_db import RolDb
from db.db_models.usuario_db import UsuarioDb
from models.autenticacion_mdl import RolCrearDto, UsuarioCrearDto


class RolNoEncontradoError(ValueError):
    """Uno o más roles solicitados no existen."""


class ServicioAutenticacion:
    """Coordina operaciones del agregado usuario y sus roles."""

    def __init__(self, sesion: AsyncSession):
        self.sesion = sesion

    async def buscar_usuario_por_correo(self, correo: str) -> UsuarioDb | None:
        resultado = await self.sesion.execute(
            select(UsuarioDb)
            .options(selectinload(UsuarioDb.roles))
            .where(UsuarioDb.correo == correo.strip().lower())
        )
        return resultado.scalar_one_or_none()

    async def autenticar(self, correo: str, contrasena: str) -> UsuarioDb | None:
        usuario = await self.buscar_usuario_por_correo(correo)
        if usuario is None or not verificar_contrasena(
            contrasena, usuario.hash_contrasena
        ):
            return None
        return usuario

    async def crear_usuario(self, datos: UsuarioCrearDto) -> UsuarioDb:
        usuario = UsuarioDb(
            nombre=datos.nombre.strip(),
            apellido=datos.apellido.strip(),
            genero=datos.genero,
            correo=datos.correo.strip().lower(),
            hash_contrasena=crear_hash_contrasena(datos.contrasena),
        )
        if datos.roles:
            usuario.roles = await self._buscar_roles(datos.roles)
        self.sesion.add(usuario)
        await self.sesion.flush()
        return usuario

    async def crear_rol(self, datos: RolCrearDto) -> RolDb:
        rol = RolDb(nombre=datos.nombre.strip(), descripcion=datos.descripcion)
        self.sesion.add(rol)
        await self.sesion.flush()
        return rol

    async def reemplazar_roles_usuario(
        self,
        usuario_id: int,
        nombres_roles: list[str],
    ) -> UsuarioDb | None:
        resultado = await self.sesion.execute(
            select(UsuarioDb)
            .options(selectinload(UsuarioDb.roles))
            .where(UsuarioDb.id == usuario_id)
        )
        usuario = resultado.scalar_one_or_none()
        if usuario is None:
            return None
        usuario.roles = await self._buscar_roles(nombres_roles)
        await self.sesion.flush()
        return usuario

    async def _buscar_roles(self, nombres_roles: list[str]) -> list[RolDb]:
        nombres = list(dict.fromkeys(nombre.strip() for nombre in nombres_roles))
        if not nombres:
            return []
        resultado = await self.sesion.execute(
            select(RolDb).where(RolDb.nombre.in_(nombres))
        )
        roles = list(resultado.scalars().all())
        encontrados = {rol.nombre for rol in roles}
        faltantes = set(nombres) - encontrados
        if faltantes:
            raise RolNoEncontradoError(
                "No existen los roles: " + ", ".join(sorted(faltantes))
            )
        return roles
