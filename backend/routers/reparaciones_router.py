"""Endpoints del CUN-01 (tomar una incidencia, registrar usos y resolverla) según el contrato v0."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from autorizacion_roles import requiere_rol
from db.database import get_db
from models.incidencia_mdl import (
    InformeResolucionCreateDto,
    InformeResolucionResponseDto,
    ReparacionResponseDto,
    UsoRepuestoCreateDto,
    UsoRepuestoResponseDto,
)
from repositories.reparaciones_repository import RepositorioReparaciones
from services.reparaciones_service import ErrorReparacion, ServicioReparaciones

router = APIRouter(prefix="/api/v0", tags=["Reparaciones"])
# Permisos acordados en docs/actores.md: el empleado repara; encargado y gerencia consultan.
reparacion = requiere_rol("empleado_mantenimiento")
lectura = requiere_rol(
    "empleado_mantenimiento", "encargado_mantenimiento", "gerencia_administracion"
)


def obtener_servicio(sesion: AsyncSession = Depends(get_db)) -> ServicioReparaciones:
    """Construye el servicio con la sesión de la solicitud."""
    return ServicioReparaciones(RepositorioReparaciones(sesion))


def error(codigo_http: int, codigo: str, mensaje: str) -> JSONResponse:
    """Construye la respuesta de error declarada en el contrato."""
    return JSONResponse(status_code=codigo_http, content={"codigo": codigo, "mensaje": mensaje})


async def rechazar(servicio: ServicioReparaciones, rechazo: ErrorReparacion) -> JSONResponse:
    """Deshace los cambios parciales de la operación antes de responder el error."""
    await servicio.repositorio.sesion.rollback()
    return error(rechazo.codigo_http, rechazo.codigo, rechazo.mensaje)


def reparacion_inexistente() -> JSONResponse:
    return error(404, "reparacion_inexistente", "Reparación inexistente.")


@router.post(
    "/incidencias/{incidencia_id}/reparacion",
    tags=["Incidencias"],
    status_code=201,
    response_model=ReparacionResponseDto,
)
async def tomar_incidencia(
    incidencia_id: int,
    usuario=Depends(reparacion),
    servicio: ServicioReparaciones = Depends(obtener_servicio),
):
    """El empleado toma la incidencia: se crea la reparación y la incidencia pasa a en reparación."""
    incidencia = await servicio.repositorio.obtener_incidencia(incidencia_id)
    if incidencia is None:
        return error(404, "incidencia_inexistente", "Incidencia inexistente.")
    try:
        return await servicio.tomar(incidencia, usuario.id)
    except ErrorReparacion as rechazo:
        return await rechazar(servicio, rechazo)


@router.get("/reparaciones/{reparacion_id}", response_model=ReparacionResponseDto)
async def obtener_reparacion(
    reparacion_id: int,
    usuario=Depends(lectura),
    servicio: ServicioReparaciones = Depends(obtener_servicio),
):
    """Obtiene el estado de una reparación, sus usos de repuestos y su informe."""
    encontrada = await servicio.repositorio.obtener_reparacion(reparacion_id)
    if encontrada is None:
        return reparacion_inexistente()
    return await servicio.serializar(encontrada)


@router.post("/reparaciones/{reparacion_id}/usos", status_code=201, response_model=UsoRepuestoResponseDto)
async def registrar_uso_repuesto(
    reparacion_id: int,
    datos: UsoRepuestoCreateDto,
    usuario=Depends(reparacion),
    servicio: ServicioReparaciones = Depends(obtener_servicio),
):
    """Registra un repuesto usado y lo descuenta del stock físico (RN-01)."""
    encontrada = await servicio.repositorio.obtener_reparacion(reparacion_id)
    if encontrada is None:
        return reparacion_inexistente()
    try:
        return await servicio.registrar_uso(encontrada, datos.model_dump(), usuario.id)
    except ErrorReparacion as rechazo:
        return await rechazar(servicio, rechazo)


@router.post(
    "/reparaciones/{reparacion_id}/informe", status_code=201, response_model=InformeResolucionResponseDto
)
async def registrar_informe_resolucion(
    reparacion_id: int,
    datos: InformeResolucionCreateDto,
    usuario=Depends(reparacion),
    servicio: ServicioReparaciones = Depends(obtener_servicio),
):
    """Registra el informe de resolución: la reparación termina y la incidencia queda resuelta."""
    encontrada = await servicio.repositorio.obtener_reparacion(reparacion_id)
    if encontrada is None:
        return reparacion_inexistente()
    try:
        return await servicio.finalizar(encontrada, datos.resumen, usuario.id)
    except ErrorReparacion as rechazo:
        return await rechazar(servicio, rechazo)
