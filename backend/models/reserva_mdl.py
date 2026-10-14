from datetime import datetime

from pydantic import AliasChoices, Field, PositiveInt

from .catalogo_mdl import RepuestoResumenDto, UbicacionResumenDto
from .common_mdl import RequestDto, ResponseDto


class ItemReservaCreateDto(RequestDto):
    repuesto_id: PositiveInt
    ubicacion_id: PositiveInt
    cantidad: PositiveInt


class ReservaCreateDto(RequestDto):
    titulo: str = Field(min_length=1, max_length=200)
    motivo: str | None = None
    planificada_para: datetime
    items: list[ItemReservaCreateDto] = Field(min_length=1)


class ItemReservaResponseDto(ResponseDto):
    id: int
    repuesto: RepuestoResumenDto = Field(
        validation_alias=AliasChoices("repuesto", "spare_part")
    )
    ubicacion: UbicacionResumenDto = Field(
        validation_alias=AliasChoices("ubicacion", "location")
    )
    cantidad: PositiveInt
    cantidad_consumida: int = Field(ge=0)


class EjecutarReservaItemDto(RequestDto):
    item_reserva_id: PositiveInt
    cantidad_consumida: PositiveInt


class EjecutarReservaDto(RequestDto):
    items: list[EjecutarReservaItemDto] = Field(min_length=1)


class ReservaResponseDto(ResponseDto):
    id: int
    creada_por_usuario_id: int
    titulo: str
    motivo: str | None = None
    planificada_para: datetime
    estado: str = Field(description="Valores sujetos a la máquina de estados de Reserva.")
    autorizada_por_usuario_id: int | None = None
    liberada_por_usuario_id: int | None = None
    creada_en: datetime
    liberada_en: datetime | None = None
    ejecutada_en: datetime | None = None
    items: list[ItemReservaResponseDto] = Field(default_factory=list)
