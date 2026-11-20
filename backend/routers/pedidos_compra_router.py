"""Endpoints de pedidos de compra según el contrato v0."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from autorizacion_roles import requiere_rol
from db.database import get_db
from models.common_mdl import PaginaResponseDto
from models.compra_mdl import (
    AsignarPedidoCompraDto,
    CancelarPedidoCompraDto,
    EstadoPedidoDto,
    PedidoCompraCreateDto,
    PedidoCompraResponseDto,
    RecepcionCompraCreateDto,
    RecepcionCompraResponseDto,
    RevisarPedidoCompraDto,
)
from repositories.pedidos_compra_repository import RepositorioPedidosCompra
from services.pedidos_compra_service import (
    ErrorPedidoCompra,
    ServicioPedidosCompra,
)

router = APIRouter(prefix="/api/v0", tags=["Pedidos de compra"])

lectura = requiere_rol("encargado_mantenimiento", "gerencia_administracion")
creacion = requiere_rol("empleado_mantenimiento", "encargado_mantenimiento")
gestion = requiere_rol("encargado_mantenimiento")


def obtener_servicio(
    sesion: AsyncSession = Depends(get_db),
) -> ServicioPedidosCompra:
    """Construye el servicio con la sesión de la solicitud."""
    return ServicioPedidosCompra(RepositorioPedidosCompra(sesion))


def error(codigo_http: int, codigo: str, mensaje: str) -> JSONResponse:
    """Construye una respuesta de error."""
    return JSONResponse(
        status_code=codigo_http,
        content={"codigo": codigo, "mensaje": mensaje},
    )


async def rechazar(
    servicio: ServicioPedidosCompra,
    rechazo: ErrorPedidoCompra,
) -> JSONResponse:
    """Deshace los cambios parciales antes de responder el error."""
    await servicio.repositorio.sesion.rollback()
    return error(rechazo.codigo_http, rechazo.codigo, rechazo.mensaje)


def pedido_inexistente() -> JSONResponse:
    return error(
        404,
        "pedido_compra_inexistente",
        "Pedido de compra inexistente.",
    )


@router.get(
    "/pedidos-compra",
    response_model=PaginaResponseDto[PedidoCompraResponseDto],
)
async def listar_pedidos_compra(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    estado: EstadoPedidoDto | None = Query(None),
    usuario=Depends(lectura),
    servicio: ServicioPedidosCompra = Depends(obtener_servicio),
):
    """Lista pedidos de compra paginados."""
    return await servicio.listar(offset, limit, estado)


@router.post(
    "/pedidos-compra",
    status_code=201,
    response_model=PedidoCompraResponseDto,
)
async def crear_pedido_compra(
    datos: PedidoCompraCreateDto,
    usuario=Depends(creacion),
    servicio: ServicioPedidosCompra = Depends(obtener_servicio),
):
    """Crea un pedido de compra."""
    try:
        return await servicio.crear(datos.model_dump(), usuario.id)
    except ErrorPedidoCompra as rechazo:
        return await rechazar(servicio, rechazo)


@router.get(
    "/pedidos-compra/{pedido_id}",
    response_model=PedidoCompraResponseDto,
)
async def obtener_pedido_compra(
    pedido_id: int,
    usuario=Depends(lectura),
    servicio: ServicioPedidosCompra = Depends(obtener_servicio),
):
    """Obtiene un pedido con sus partidas y recepciones."""
    pedido = await servicio.repositorio.obtener_pedido(pedido_id)

    if pedido is None:
        return pedido_inexistente()

    return (await servicio.serializar([pedido]))[0]


@router.post(
    "/pedidos-compra/{pedido_id}/asignacion",
    response_model=PedidoCompraResponseDto,
)
async def asignar_pedido_compra(
    pedido_id: int,
    datos: AsignarPedidoCompraDto,
    usuario=Depends(gestion),
    servicio: ServicioPedidosCompra = Depends(obtener_servicio),
):
    """Asigna un pedido para su revisión."""
    pedido = await servicio.repositorio.obtener_pedido(pedido_id)

    if pedido is None:
        return pedido_inexistente()

    try:
        return await servicio.asignar(pedido, datos.model_dump())
    except ErrorPedidoCompra as rechazo:
        return await rechazar(servicio, rechazo)


@router.post(
    "/pedidos-compra/{pedido_id}/revision",
    response_model=PedidoCompraResponseDto,
)
async def revisar_pedido_compra(
    pedido_id: int,
    datos: RevisarPedidoCompraDto,
    usuario=Depends(gestion),
    servicio: ServicioPedidosCompra = Depends(obtener_servicio),
):
    """Registra la revisión del pedido."""
    pedido = await servicio.repositorio.obtener_pedido(pedido_id)

    if pedido is None:
        return pedido_inexistente()

    try:
        return await servicio.revisar(
            pedido,
            datos.model_dump(),
            usuario.id,
        )
    except ErrorPedidoCompra as rechazo:
        return await rechazar(servicio, rechazo)


@router.post(
    "/pedidos-compra/{pedido_id}/aprobacion",
    response_model=PedidoCompraResponseDto,
)
async def aprobar_pedido_compra(
    pedido_id: int,
    datos: RevisarPedidoCompraDto,
    usuario=Depends(gestion),
    servicio: ServicioPedidosCompra = Depends(obtener_servicio),
):
    """Aprueba un pedido pendiente de aprobación."""
    pedido = await servicio.repositorio.obtener_pedido(pedido_id)

    if pedido is None:
        return pedido_inexistente()

    try:
        return await servicio.aprobar(
            pedido,
            datos.model_dump(),
            usuario.id,
        )
    except ErrorPedidoCompra as rechazo:
        return await rechazar(servicio, rechazo)


@router.post(
    "/pedidos-compra/{pedido_id}/cancelacion",
    response_model=PedidoCompraResponseDto,
)
async def cancelar_pedido_compra(
    pedido_id: int,
    datos: CancelarPedidoCompraDto,
    usuario=Depends(gestion),
    servicio: ServicioPedidosCompra = Depends(obtener_servicio),
):
    """Cancela un pedido de compra."""
    pedido = await servicio.repositorio.obtener_pedido(pedido_id)

    if pedido is None:
        return pedido_inexistente()

    try:
        return await servicio.cancelar(pedido, datos.model_dump())
    except ErrorPedidoCompra as rechazo:
        return await rechazar(servicio, rechazo)


@router.post(
    "/pedidos-compra/{pedido_id}/confirmacion",
    response_model=PedidoCompraResponseDto,
)
async def confirmar_pedido_compra(
    pedido_id: int,
    usuario=Depends(gestion),
    servicio: ServicioPedidosCompra = Depends(obtener_servicio),
):
    """Confirma el pedido aprobado para habilitar su recepción."""
    pedido = await servicio.repositorio.obtener_pedido(pedido_id)

    if pedido is None:
        return pedido_inexistente()

    try:
        return await servicio.confirmar(pedido)
    except ErrorPedidoCompra as rechazo:
        return await rechazar(servicio, rechazo)


@router.post(
    "/pedidos-compra/{pedido_id}/recepciones",
    status_code=201,
    response_model=RecepcionCompraResponseDto,
    tags=["Recepciones"],
)
async def registrar_recepcion_compra(
    pedido_id: int,
    datos: RecepcionCompraCreateDto,
    usuario=Depends(gestion),
    servicio: ServicioPedidosCompra = Depends(obtener_servicio),
):
    """Registra la recepción y actualiza el stock físico."""
    pedido = await servicio.repositorio.obtener_pedido(pedido_id)

    if pedido is None:
        return pedido_inexistente()

    try:
        return await servicio.recibir(
            pedido,
            datos.model_dump(),
            usuario.id,
        )
    except ErrorPedidoCompra as rechazo:
        return await rechazar(servicio, rechazo)
