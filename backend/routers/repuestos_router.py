"""Endpoints de repuestos y ubicaciones según el contrato v0."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from autorizacion_roles import requiere_rol
from db.database import get_db
from db.db_models.catalogo import UbicacionDb
from models.catalogo_mdl import (
    RepuestoCreateDto,
    RepuestoResponseDto,
    RepuestoUpdateDto,
    UbicacionCreateDto,
    UbicacionResponseDto,
)
from models.common_mdl import PaginaResponseDto
from repositories.repuestos_repository import RepositorioRepuestos
from services.repuestos_service import ServicioRepuestos

router = APIRouter(prefix="/api/v0")
# Permisos acordados en docs/actores.md: el operario no accede al almacén.
lectura = requiere_rol(
    "empleado_mantenimiento", "encargado_mantenimiento", "gerencia_administracion"
)
escritura = requiere_rol("empleado_mantenimiento", "encargado_mantenimiento")
alta_repuesto = requiere_rol("encargado_mantenimiento")


def obtener_servicio(sesion: AsyncSession = Depends(get_db)) -> ServicioRepuestos:
    """Construye el servicio con la sesión de la solicitud."""
    return ServicioRepuestos(RepositorioRepuestos(sesion))


def error(codigo_http: int, codigo: str, mensaje: str) -> JSONResponse:
    """Construye la respuesta de error declarada en el contrato."""
    return JSONResponse(status_code=codigo_http, content={"codigo": codigo, "mensaje": mensaje})


def repuesto_inexistente() -> JSONResponse:
    return error(404, "repuesto_inexistente", "Repuesto inexistente.")


@router.get("/repuestos", tags=["Repuestos"], response_model=PaginaResponseDto[RepuestoResponseDto])
async def listar_repuestos(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    buscar: str | None = Query(None, description="Nombre, descripción o código QR/de barras."),
    usuario=Depends(lectura),
    servicio: ServicioRepuestos = Depends(obtener_servicio),
):
    """Lista repuestos paginados con sus existencias por ubicación."""
    return await servicio.listar(offset, limit, buscar)


@router.post("/repuestos", tags=["Repuestos"], status_code=201, response_model=RepuestoResponseDto)
async def crear_repuesto(
    datos: RepuestoCreateDto,
    usuario=Depends(alta_repuesto),
    servicio: ServicioRepuestos = Depends(obtener_servicio),
):
    """Incorpora un repuesto al catálogo sin existencias iniciales."""
    try:
        return await servicio.crear(datos.model_dump())
    except IntegrityError:
        await servicio.repositorio.sesion.rollback()
        return error(409, "duplicado", "Ya existe un repuesto con ese código.")


@router.get(
    "/repuestos/codigo/{codigo}", tags=["Repuestos"], response_model=RepuestoResponseDto
)
async def buscar_repuesto_por_codigo(
    codigo: str,
    usuario=Depends(lectura),
    servicio: ServicioRepuestos = Depends(obtener_servicio),
):
    """Busca un repuesto por su código QR o de barras."""
    repuesto = await servicio.repositorio.obtener_repuesto_por_codigo(codigo)
    if repuesto is None:
        return repuesto_inexistente()
    return (await servicio.serializar([repuesto]))[0]


@router.get("/repuestos/{repuesto_id}", tags=["Repuestos"], response_model=RepuestoResponseDto)
async def obtener_repuesto(
    repuesto_id: int,
    usuario=Depends(lectura),
    servicio: ServicioRepuestos = Depends(obtener_servicio),
):
    """Obtiene los datos y el resumen de stock de un repuesto."""
    repuesto = await servicio.repositorio.obtener_repuesto(repuesto_id)
    if repuesto is None:
        return repuesto_inexistente()
    return (await servicio.serializar([repuesto]))[0]


@router.patch("/repuestos/{repuesto_id}", tags=["Repuestos"], response_model=RepuestoResponseDto)
async def actualizar_repuesto(
    repuesto_id: int,
    datos: RepuestoUpdateDto,
    usuario=Depends(escritura),
    servicio: ServicioRepuestos = Depends(obtener_servicio),
):
    """Actualiza parcialmente la información de catálogo de un repuesto."""
    repuesto = await servicio.repositorio.obtener_repuesto(repuesto_id)
    if repuesto is None:
        return repuesto_inexistente()
    cambios = datos.model_dump(exclude_unset=True)
    for campo in ("codigo", "nombre", "stock_minimo", "activo"):
        if campo in cambios and cambios[campo] is None:
            return error(422, "valor_invalido", f"{campo} no puede ser nulo.")
    try:
        return await servicio.actualizar(repuesto, cambios)
    except IntegrityError:
        await servicio.repositorio.sesion.rollback()
        return error(409, "duplicado", "Ya existe un repuesto con ese código.")


@router.get("/ubicaciones", tags=["Ubicaciones"], response_model=PaginaResponseDto[UbicacionResponseDto])
async def listar_ubicaciones(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    usuario=Depends(lectura),
    servicio: ServicioRepuestos = Depends(obtener_servicio),
):
    """Lista las ubicaciones del almacén."""
    items, total = await servicio.repositorio.listar_ubicaciones(offset, limit)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.post("/ubicaciones", tags=["Ubicaciones"], status_code=201, response_model=UbicacionResponseDto)
async def crear_ubicacion(
    datos: UbicacionCreateDto,
    usuario=Depends(escritura),
    servicio: ServicioRepuestos = Depends(obtener_servicio),
):
    """Crea una ubicación identificable para almacenar stock."""
    try:
        return await servicio.repositorio.guardar(UbicacionDb(**datos.model_dump()))
    except IntegrityError:
        await servicio.repositorio.sesion.rollback()
        return error(409, "duplicado", "Ya existe una ubicación con ese código.")
