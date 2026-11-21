"""Comando que ejecuta en orden las etapas de carga de datos de prueba."""

from __future__ import annotations

import asyncio
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import typer
from sqlalchemy import delete, func, select

from db.database import dispose_db, get_sessionmaker, init_db
from db.db_models import (
    FotoIncidenciaDb,
    IncidenciaDb,
    InformeResolucionDb,
    ItemPedidoCompraDb,
    ItemRecepcionCompraDb,
    ItemReservaDb,
    MaquinaDb,
    MovimientoStockDb,
    PedidoCompraDb,
    RecepcionCompraDb,
    ReparacionDb,
    RepuestoDb,
    RepuestoXUbicacionDb,
    ReservaDb,
    RolDb,
    TipoMaquinaDb,
    TipoMaquinaXRepuestoDb,
    UbicacionDb,
    UsoRepuestoReparacionDb,
)
from services.autenticacion_service import ServicioAutenticacion
from utils import load_config


from dummy_db import paso_01_usuarios, paso_02_catalogo, paso_03_incidencias, paso_04_compras, paso_05_stock

aplicacion = typer.Typer(help="Carga datos de prueba del dominio en la base configurada.")


# Las tablas del dominio, en orden seguro para borrar con claves foráneas activas.
TABLAS_DOMINIO = (
    MovimientoStockDb,
    ItemReservaDb,
    ReservaDb,
    ItemRecepcionCompraDb,
    RecepcionCompraDb,
    ItemPedidoCompraDb,
    PedidoCompraDb,
    InformeResolucionDb,
    UsoRepuestoReparacionDb,
    ReparacionDb,
    FotoIncidenciaDb,
    IncidenciaDb,
    RepuestoXUbicacionDb,
    TipoMaquinaXRepuestoDb,
    RepuestoDb,
    UbicacionDb,
    MaquinaDb,
    TipoMaquinaDb,
)

async def _cargar_dominio(sesion, usuarios):
    ahora = datetime.now(timezone.utc)
    contexto = await paso_02_catalogo.cargar(sesion, ahora)
    contexto.update(ahora=ahora, usuarios=usuarios, fisico=defaultdict(int),
                    reservado=defaultdict(int), movimientos=[],
                    ubicacion_de={codigo: ubicacion for codigo, *_, ubicacion, _ in paso_02_catalogo.REPUESTOS})
    await paso_03_incidencias.cargar(sesion, contexto)
    await paso_04_compras.cargar(sesion, contexto)
    await paso_05_stock.cargar(sesion, contexto)
    return {
        "máquinas": len(contexto["maquinas"]),
        "ubicaciones": len(contexto["ubicaciones"]),
        "repuestos": len(contexto["repuestos"]),
        "incidencias": len(contexto["incidencias"]),
        "reparaciones": len(paso_03_incidencias.REPARACIONES),
        "pedidos de compra": len(paso_04_compras.PEDIDOS_COMPRA),
        "movimientos de stock": len(contexto["movimientos"]),
    }


async def _hay_datos(sesion) -> bool:
    return bool(
        await sesion.scalar(select(func.count()).select_from(MaquinaDb))
        or await sesion.scalar(select(func.count()).select_from(RepuestoDb))
    )


async def _ejecutar(nombre_configuracion: str, reiniciar: bool) -> str:
    configuracion = load_config(nombre_configuracion, reload=True)
    base = configuracion.database
    if base.DB_TYPE.lower() in ("sqlite", "sqlite3"):
        destino = base.DB_NAME if base.DB_NAME == ":memory:" else str(Path(base.DB_NAME).resolve())
    else:
        destino = f"{base.DB_TYPE}://{base.DB_HOST}:{base.DB_PORT}/{base.DB_NAME}"
    typer.echo(f"Base de datos configurada: {destino}")
    await init_db()
    try:
        async with get_sessionmaker()() as sesion:
            if reiniciar:
                for tabla in TABLAS_DOMINIO:
                    await sesion.execute(delete(tabla))
            elif await _hay_datos(sesion):
                return "La base ya tiene datos del dominio; no se cargó nada. Usá --recreate para recargarlos."
            usuarios = await paso_01_usuarios._asegurar_usuarios(ServicioAutenticacion(sesion))
            cantidades = await _cargar_dominio(sesion, usuarios)
            await sesion.commit()
    finally:
        await dispose_db()
    detalle = ", ".join(f"{cantidad} {nombre}" for nombre, cantidad in cantidades.items())
    return f"Datos de prueba cargados: {detalle}."


@aplicacion.command()
def cargar(
    reiniciar: bool = typer.Option(
        False, "--recreate", help="Borra los datos del dominio antes de cargar. No toca usuarios ni roles."
    ),
    sin_confirmar: bool = typer.Option(False, "--si", "-y", help="No pedir confirmación al reiniciar."),
    configuracion: str = typer.Option("default", "--config", "-c", help="Nombre del entorno, por ejemplo dev para config.dev.toml."),
) -> None:
    """Carga máquinas, stock, incidencias, reparaciones, compras y reservas de prueba."""

    if not re.fullmatch(r"[A-Za-z0-9_-]+", configuracion):
        raise typer.BadParameter("Indicá un nombre de entorno, por ejemplo dev.", param_hint="--config")

    if reiniciar and not sin_confirmar:
        typer.confirm(
            "Se borran todas las máquinas, repuestos, incidencias, compras y reservas. ¿Continuar?",
            abort=True,
        )
    try:
        typer.echo(asyncio.run(_ejecutar(configuracion, reiniciar)))
    except Exception as error:
        typer.secho(str(error), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    aplicacion()
