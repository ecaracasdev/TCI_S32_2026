"""Lista usuarios y roles de la base configurada."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.database import dispose_db, get_sessionmaker
from db.db_models.usuario_db import UsuarioDb
from gestionar_acceso import _mostrar_error
from utils import load_config


aplicacion = typer.Typer(help="Lista usuarios y sus roles.")


async def _consultar(config: str) -> list[tuple[int, str, str, str]]:
    """Consulta usuarios y roles sin modificar ni inicializar el esquema."""
    load_config(config, reload=True)
    try:
        async with get_sessionmaker()() as sesion:
            resultado = await sesion.execute(
                select(UsuarioDb).options(selectinload(UsuarioDb.roles)).order_by(UsuarioDb.id)
            )
            return [
                (usuario.id, usuario.correo, f"{usuario.nombre} {usuario.apellido}".strip(),
                 ", ".join(sorted(rol.nombre for rol in usuario.roles)) or "Sin roles")
                for usuario in resultado.scalars().all()
            ]
    finally:
        await dispose_db()


@aplicacion.command()
def listar(
    config: str = typer.Option("default", "--config", "-c", help="Nombre del entorno TOML."),
) -> None:
    """Muestra el ID, correo, nombre y roles de cada usuario."""
    try:
        usuarios = asyncio.run(_consultar(config))
    except Exception as error:
        _mostrar_error(error)

    if not usuarios:
        typer.echo("No hay usuarios registrados.")
        return
    tabla = Table("ID", "Correo", "Nombre", "Roles")
    for usuario_id, correo, nombre, roles in usuarios:
        tabla.add_row(str(usuario_id), correo, nombre, roles)
    Console().print(tabla)


def ejecutar() -> None:
    """Ejecuta el comando registrado en el proyecto."""
    aplicacion()


if __name__ == "__main__":
    ejecutar()
