"""Comando para agregar un rol existente a un usuario por correo."""

import asyncio

import typer

from gestionar_acceso import _ejecutar, _mostrar_error
from services.autenticacion_service import ServicioAutenticacion


aplicacion = typer.Typer(help="Asigna un rol sin modificar los roles existentes.")


@aplicacion.command()
def asignar(
    user: str = typer.Option(..., "--user", help="Correo del usuario."),
    role: str = typer.Option(..., "--role", help="Nombre de un rol existente."),
    config: str = typer.Option("default", "--config", "-c", help="Nombre del entorno TOML."),
) -> None:
    """Agrega un rol al usuario; si ya lo tiene, no hace cambios."""
    correo, nombre_rol = user.strip(), role.strip()
    if not correo or not nombre_rol:
        raise typer.BadParameter("El usuario y el rol no pueden estar vacíos.")

    async def operacion(servicio: ServicioAutenticacion) -> str:
        usuario, creado = await servicio.asignar_rol_por_correo(correo, nombre_rol)
        if creado:
            return f"Rol '{nombre_rol}' asignado a {usuario.correo}."
        return f"El usuario {usuario.correo} ya tiene el rol '{nombre_rol}'."

    try:
        typer.echo(asyncio.run(_ejecutar(config, operacion)))
    except Exception as error:
        _mostrar_error(error)


def ejecutar() -> None:
    """Ejecuta el comando registrado como script del proyecto."""
    aplicacion()


if __name__ == "__main__":
    ejecutar()
