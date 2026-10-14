from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, Field, PositiveInt

from .catalogo_mdl import MaquinaResponseDto, RepuestoResumenDto
from .common_mdl import RequestDto, ResponseDto


TurnoDto = Literal["manana", "tarde", "noche"]


class FotoIncidenciaDto(ResponseDto):
    id: int
    nombre_archivo: str | None = None
    tipo_mime: str
    capturada_en: datetime | None = None
    contenido_base64: str


class FotoIncidenciaCreateDto(RequestDto):
    contenido_base64: str = Field(min_length=1)
    nombre_archivo: str | None = Field(default=None, max_length=255)
    tipo_mime: str = Field(min_length=1, max_length=100)
    capturada_en: datetime | None = None


class IncidenciaCreateDto(RequestDto):
    maquina_codigo: str = Field(min_length=1, max_length=100, description="Código QR o de barras.")
    descripcion: str = Field(min_length=1)
    turno: TurnoDto
    fotos: list[FotoIncidenciaCreateDto] = Field(default_factory=list)


class IncidenciaResponseDto(ResponseDto):
    id: int
    maquina_id: int
    maquina: MaquinaResponseDto = Field(
        validation_alias=AliasChoices("maquina", "machine")
    )
    reportada_por_usuario_id: int
    descripcion: str
    estado: str = Field(description="Valores sujetos a la máquina de estados T01.")
    turno: TurnoDto
    reportada_en: datetime
    resuelta_en: datetime | None = None
    fotos: list[FotoIncidenciaDto] = Field(
        default_factory=list,
        validation_alias=AliasChoices("fotos", "photos"),
    )


class UsoRepuestoCreateDto(RequestDto):
    repuesto_id: PositiveInt
    cantidad: PositiveInt
    ubicacion_id: PositiveInt | None = Field(
        default=None,
        description="Ubicación preferida para descontar stock. Si se omite, el servicio define la asignación.",
    )


class UsoRepuestoResponseDto(ResponseDto):
    id: int
    reparacion_id: int
    repuesto: RepuestoResumenDto = Field(
        validation_alias=AliasChoices("repuesto", "spare_part")
    )
    cantidad: PositiveInt
    usada_por_usuario_id: int
    usada_en: datetime


class InformeResolucionCreateDto(RequestDto):
    resumen: str = Field(min_length=1)


class InformeResolucionResponseDto(ResponseDto):
    id: int
    reparacion_id: int
    empleado_id: int
    resumen: str
    creada_en: datetime


class ReparacionResponseDto(ResponseDto):
    id: int
    incidencia_id: int
    empleado_id: int | None = None
    estado: str = Field(description="Estado sujeto a la máquina de estados del dominio.")
    iniciada_en: datetime | None = None
    completada_en: datetime | None = None
    usos: list[UsoRepuestoResponseDto] = Field(
        default_factory=list,
        validation_alias=AliasChoices("usos", "part_usages"),
    )
    informe_resolucion: InformeResolucionResponseDto | None = Field(
        default=None,
        validation_alias=AliasChoices("informe_resolucion", "resolution_report"),
    )
