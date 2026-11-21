"""Lista los roles disponibles en la base configurada."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import select

from db.database import dispose_db, get_sessionmaker
from db.db_models.rol_db import RolDb
from gestionar_acceso import _mostrar_error
from utils import load_config


aplicacion = typer.Typer(help="Lista los roles disponibles.")


async def _consultar(config: str) -> list[tuple[int, str, str]]:
    """Consulta el catálogo de roles sin inicializar ni modificar la base."""
    load_config(config, reload=True)
    try:
        async with get_sessionmaker()() as sesion:
            resultado = await sesion.execute(
                select(RolDb.id, RolDb.nombre, RolDb.descripcion).order_by(RolDb.nombre)
            )
            return [(id_rol, nombre, descripcion or "") for id_rol, nombre, descripcion in resultado]
    finally:
        await dispose_db()


@aplicacion.command()
def listar(
    config: str = typer.Option("default", "--config", "-c", help="Nombre del entorno TOML."),
) -> None:
    """Muestra el ID, nombre y descripción de cada rol."""
    try:
        roles = asyncio.run(_consultar(config))
    except Exception as error:
        _mostrar_error(error)

    if not roles:
        typer.echo("No hay roles registrados.")
        return
    tabla = Table("ID", "Rol", "Descripción")
    for id_rol, nombre, descripcion in roles:
        tabla.add_row(str(id_rol), nombre, descripcion)
    Console().print(tabla)


def ejecutar() -> None:
    """Ejecuta el comando registrado en el proyecto."""
    aplicacion()


if __name__ == "__main__":
    ejecutar()
