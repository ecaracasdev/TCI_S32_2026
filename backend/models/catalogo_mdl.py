from datetime import datetime

from pydantic import AliasChoices, Field, PositiveInt, computed_field

from .common_mdl import RequestDto, ResponseDto


class TipoMaquinaResumenDto(ResponseDto):
    id: int
    nombre: str


class TipoMaquinaResponseDto(TipoMaquinaResumenDto):
    descripcion: str | None = None
    activo: bool


class TipoMaquinaCreateDto(RequestDto):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str | None = None


class UbicacionResumenDto(ResponseDto):
    id: int
    codigo: str
    descripcion: str | None = None


class UbicacionResponseDto(UbicacionResumenDto):
    activo: bool


class UbicacionCreateDto(RequestDto):
    codigo: str = Field(min_length=1, max_length=50, examples=["A-03-12"])
    descripcion: str | None = Field(default=None, max_length=255)


class MaquinaResponseDto(ResponseDto):
    id: int
    codigo: str
    tipo_maquina_id: int
    tipo_maquina: TipoMaquinaResumenDto = Field(
        validation_alias=AliasChoices("tipo_maquina", "machine_type")
    )
    numero_serie: str | None = None
    estado: str = Field(description="Estado definido por la máquina de estados del dominio.")
    fecha_instalacion: datetime | None = None
    creado_en: datetime
    actualizado_en: datetime | None = None


class MaquinaCreateDto(RequestDto):
    codigo: str = Field(min_length=1, max_length=100)
    tipo_maquina_id: PositiveInt
    numero_serie: str | None = Field(default=None, max_length=100)
    fecha_instalacion: datetime | None = None


class MaquinaUpdateDto(RequestDto):
    codigo: str | None = Field(default=None, min_length=1, max_length=100)
    tipo_maquina_id: PositiveInt | None = None
    numero_serie: str | None = Field(default=None, max_length=100)
    estado: str | None = None
    fecha_instalacion: datetime | None = None


class RepuestoResumenDto(ResponseDto):
    id: int
    codigo: str
    nombre: str


class StockUbicacionResponseDto(ResponseDto):
    ubicacion_id: int
    ubicacion: UbicacionResumenDto = Field(
        validation_alias=AliasChoices("ubicacion", "location")
    )
    cantidad_fisica: int = Field(ge=0)
    cantidad_reservada: int = Field(ge=0)

    @computed_field
    @property
    def cantidad_disponible(self) -> int:
        return self.cantidad_fisica - self.cantidad_reservada


class RepuestoResponseDto(ResponseDto):
    id: int
    codigo: str
    nombre: str
    descripcion: str | None = None
    stock_minimo: int = Field(ge=0)
    activo: bool
    creado_en: datetime
    actualizado_en: datetime | None = None
    stock: list[StockUbicacionResponseDto] = Field(
        default_factory=list,
        validation_alias=AliasChoices("stock", "stocks"),
    )

    @computed_field
    @property
    def stock_fisico_total(self) -> int:
        return sum(stock.cantidad_fisica for stock in self.stock)

    @computed_field
    @property
    def stock_reservado_total(self) -> int:
        return sum(stock.cantidad_reservada for stock in self.stock)

    @computed_field
    @property
    def stock_disponible_total(self) -> int:
        return sum(stock.cantidad_disponible for stock in self.stock)


class RepuestoCreateDto(RequestDto):
    codigo: str = Field(min_length=1, max_length=100)
    nombre: str = Field(min_length=1, max_length=200)
    descripcion: str | None = None
    stock_minimo: int = Field(default=0, ge=0)


class RepuestoUpdateDto(RequestDto):
    codigo: str | None = Field(default=None, min_length=1, max_length=100)
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    descripcion: str | None = None
    stock_minimo: int | None = Field(default=None, ge=0)
    activo: bool | None = None
