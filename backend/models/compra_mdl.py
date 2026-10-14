from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, Field, PositiveInt

from .catalogo_mdl import RepuestoResumenDto, UbicacionResumenDto
from .common_mdl import RequestDto, ResponseDto


UrgenciaPedidoDto = Literal["normal", "urgente"]
OrigenPedidoDto = Literal["manual", "automatico"]
EstadoPedidoDto = Literal[
    "creado",
    "pendiente_revision",
    "pendiente_aprobacion",
    "confirmado",
    "cancelado",
    "pendiente_recepcion",
    "recibido",
]


class ItemPedidoCompraCreateDto(RequestDto):
    repuesto_id: PositiveInt
    cantidad_solicitada: PositiveInt


class ItemPedidoCompraResponseDto(ResponseDto):
    id: int
    repuesto: RepuestoResumenDto = Field(
        validation_alias=AliasChoices("repuesto", "spare_part")
    )
    cantidad_solicitada: PositiveInt


class PedidoCompraCreateDto(RequestDto):
    urgencia: UrgenciaPedidoDto = "normal"
    motivo: str | None = None
    items: list[ItemPedidoCompraCreateDto] = Field(min_length=1)


class PedidoCompraResponseDto(ResponseDto):
    id: int
    creada_por_usuario_id: int
    asignado_a_usuario_id: int | None = None
    revision_resuelta_por_usuario_id: int | None = None
    revision_resuelta_en: datetime | None = None
    urgencia: UrgenciaPedidoDto
    origen: OrigenPedidoDto
    estado: EstadoPedidoDto
    motivo: str | None = None
    motivo_cancelacion: str | None = None
    creado_en: datetime
    items: list[ItemPedidoCompraResponseDto] = Field(default_factory=list)
    recepciones: list["RecepcionCompraResponseDto"] = Field(
        default_factory=list,
        validation_alias=AliasChoices("recepciones", "receipts"),
    )


class AsignarPedidoCompraDto(RequestDto):
    asignado_a_usuario_id: PositiveInt


class RevisarPedidoCompraDto(RequestDto):
    observaciones: str | None = None


class CancelarPedidoCompraDto(RequestDto):
    motivo: str = Field(min_length=1)


class ItemRecepcionCompraCreateDto(RequestDto):
    item_pedido_compra_id: PositiveInt
    ubicacion_id: PositiveInt
    cantidad: PositiveInt


class RecepcionCompraCreateDto(RequestDto):
    delegada_a_usuario_id: PositiveInt | None = None
    notas: str | None = None
    items: list[ItemRecepcionCompraCreateDto] = Field(min_length=1)


class ItemRecepcionCompraResponseDto(ResponseDto):
    id: int
    item_pedido_compra_id: int
    ubicacion: UbicacionResumenDto = Field(
        validation_alias=AliasChoices("ubicacion", "location")
    )
    cantidad: PositiveInt


class RecepcionCompraResponseDto(ResponseDto):
    id: int
    pedido_compra_id: int
    recibida_por_usuario_id: int
    delegada_a_usuario_id: int | None = None
    recibida_en: datetime
    notas: str | None = None
    items: list[ItemRecepcionCompraResponseDto] = Field(default_factory=list)
