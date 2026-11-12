"""Comandos locales para aprovisionar usuarios y roles sin exponerlos por HTTP."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

import typer
from sqlalchemy.exc import IntegrityError

from db.database import dispose_db, get_sessionmaker, init_db
from models.autenticacion_mdl import RolCrearDto, UsuarioCrearDto
from services.autenticacion_service import ServicioAutenticacion
from utils import load_config


aplicacion = typer.Typer(help="Aprovisiona usuarios y roles del backend.")


async def _ejecutar(
    nombre_configuracion: str,
    operacion: Callable[[ServicioAutenticacion], Awaitable[str]],
) -> str:
    load_config(nombre_configuracion, reload=True)
    await init_db()
    try:
        async with get_sessionmaker()() as sesion:
            resultado = await operacion(ServicioAutenticacion(sesion))
            await sesion.commit()
            return resultado
    finally:
        await dispose_db()


def _mostrar_error(error: Exception) -> None:
    typer.secho(str(error), fg=typer.colors.RED, err=True)
    raise typer.Exit(code=1)


@aplicacion.command("crear-rol")
def crear_rol(
    nombre: str = typer.Argument(..., help="Nombre estable del rol."),
    descripcion: str | None = typer.Option(None, help="Descripción opcional."),
    configuracion: str = typer.Option("default", "--config", help="Entorno TOML."),
) -> None:
    async def operacion(servicio: ServicioAutenticacion) -> str:
        rol = await servicio.crear_rol(
            RolCrearDto(nombre=nombre, descripcion=descripcion)
        )
        return f"Rol creado: {rol.nombre}"

    try:
        typer.echo(asyncio.run(_ejecutar(configuracion, operacion)))
    except IntegrityError:
        _mostrar_error(f"Ya existe el rol '{nombre}'.")
    except Exception as error:
        _mostrar_error(error)


@aplicacion.command("crear-usuario")
def crear_usuario(
    nombre: str = typer.Option(..., prompt=True, help="Nombre."),
    apellido: str = typer.Option(..., prompt=True, help="Apellido."),
    genero: str = typer.Option(..., prompt=True, help="Código de género de un carácter."),
    correo: str = typer.Option(..., prompt=True, help="Correo de acceso."),
    roles: list[str] = typer.Option([], "--rol", help="Rol asignado; repetir para varios."),
    configuracion: str = typer.Option("default", "--config", help="Entorno TOML."),
) -> None:
    contrasena = typer.prompt(
        "Contraseña de acceso",
        hide_input=True,
        confirmation_prompt=True,
    )

    async def operacion(servicio: ServicioAutenticacion) -> str:
        usuario = await servicio.crear_usuario(
            UsuarioCrearDto(
                nombre=nombre,
                apellido=apellido,
                genero=genero,
                correo=correo,
                contrasena=contrasena,
                roles=roles,
            )
        )
        return f"Usuario creado: {usuario.id} ({usuario.correo})"

    try:
        typer.echo(asyncio.run(_ejecutar(configuracion, operacion)))
    except IntegrityError:
        _mostrar_error(f"Ya existe el usuario '{correo}'.")
    except Exception as error:
        _mostrar_error(error)


@aplicacion.command("reemplazar-roles")
def reemplazar_roles(
    usuario_id: int = typer.Argument(..., min=1),
    roles: list[str] = typer.Option(..., "--rol", help="Rol asignado; repetir para varios."),
    configuracion: str = typer.Option("default", "--config", help="Entorno TOML."),
) -> None:
    async def operacion(servicio: ServicioAutenticacion) -> str:
        usuario = await servicio.reemplazar_roles_usuario(usuario_id, roles)
        if usuario is None:
            raise ValueError(f"No existe el usuario {usuario_id}.")
        nombres = ", ".join(rol.nombre for rol in usuario.roles) or "sin roles"
        return f"Roles actualizados para {usuario.correo}: {nombres}"

    try:
        typer.echo(asyncio.run(_ejecutar(configuracion, operacion)))
    except IntegrityError as error:
        _mostrar_error(error)
    except Exception as error:
        _mostrar_error(error)


if __name__ == "__main__":
    aplicacion()
