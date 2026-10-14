from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, Field, PositiveInt

from .catalogo_mdl import RepuestoResumenDto, UbicacionResumenDto
from .common_mdl import ResponseDto


TipoMovimientoDto = Literal["entrada", "salida", "reserva", "liberacion", "consumo"]


class AlertaStockResponseDto(ResponseDto):
    repuesto: RepuestoResumenDto
    stock_disponible: int = Field(ge=0)
    stock_minimo: int = Field(ge=0)


class MovimientoStockResponseDto(ResponseDto):
    id: int
    repuesto: RepuestoResumenDto = Field(
        validation_alias=AliasChoices("repuesto", "spare_part")
    )
    ubicacion: UbicacionResumenDto = Field(
        validation_alias=AliasChoices("ubicacion", "location")
    )
    tipo_movimiento: TipoMovimientoDto
    cantidad: PositiveInt
    variacion_fisica: int
    variacion_reservada: int
    realizado_por_usuario_id: int
    ocurrido_en: datetime
    motivo: str | None = None
    item_recepcion_compra_id: int | None = None
    uso_repuesto_reparacion_id: int | None = None
    item_reserva_id: int | None = None
