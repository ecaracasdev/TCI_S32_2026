from datetime import datetime

from sqlalchemy import CheckConstraint, Index, Text, text
from sqlmodel import Field, SQLModel

from .fechas import fecha_actual


class TipoMaquinaDb(SQLModel, table=True):
    __tablename__ = "tipos_maquina"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, max_length=100)
    descripcion: str | None = Field(default=None, sa_type=Text)
    activo: bool = Field(default=True, sa_column_kwargs={"server_default": text("true")})


class MaquinaDb(SQLModel, table=True):
    __tablename__ = "maquinas"

    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, max_length=100)
    tipo_maquina_id: int = Field(foreign_key="tipos_maquina.id")
    numero_serie: str | None = Field(default=None, unique=True, max_length=100)
    estado: str = Field(max_length=50, default='activa', sa_column_kwargs={"server_default": text("'activa'")})
    fecha_instalacion: datetime | None = Field(default=None)
    creado_en: datetime = Field(default_factory=fecha_actual, sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})
    actualizado_en: datetime | None = Field(default=None)


class UbicacionDb(SQLModel, table=True):
    __tablename__ = "ubicaciones"

    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, max_length=50)
    descripcion: str | None = Field(default=None, max_length=255)
    activo: bool = Field(default=True, sa_column_kwargs={"server_default": text("true")})


class RepuestoDb(SQLModel, table=True):
    __tablename__ = "repuestos"
    __table_args__ = (
        CheckConstraint("stock_minimo >= 0", name="repuestos_stock_minimo_no_negativo"),
    )

    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, max_length=100)
    nombre: str = Field(max_length=200)
    descripcion: str | None = Field(default=None, sa_type=Text)
    stock_minimo: int = Field(default=0, sa_column_kwargs={"server_default": text("0")})
    activo: bool = Field(default=True, sa_column_kwargs={"server_default": text("true")})
    creado_en: datetime = Field(default_factory=fecha_actual, sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})
    actualizado_en: datetime | None = Field(default=None)


class TipoMaquinaXRepuestoDb(SQLModel, table=True):
    __tablename__ = "tipos_maquina_x_repuestos"
    __table_args__ = (
        CheckConstraint("cantidad_minima >= 1", name="tipos_maquina_x_repuestos_cantidad_minima_positiva"),
        Index("ix_tipos_maquina_x_repuestos_repuesto_id", "repuesto_id"),
    )

    tipo_maquina_id: int = Field(primary_key=True, foreign_key="tipos_maquina.id")
    repuesto_id: int = Field(primary_key=True, foreign_key="repuestos.id")
    cantidad_minima: int = Field(default=1, sa_column_kwargs={"server_default": text("1")})


class RepuestoXUbicacionDb(SQLModel, table=True):
    __tablename__ = "repuestos_x_ubicaciones"
    __table_args__ = (
        CheckConstraint("cantidad_fisica >= 0", name="repuestos_x_ubicaciones_fisico_no_negativo"),
        CheckConstraint("cantidad_reservada >= 0", name="repuestos_x_ubicaciones_reservado_no_negativo"),
        CheckConstraint("cantidad_reservada <= cantidad_fisica", name="repuestos_x_ubicaciones_reservado_dentro_fisico"),
        Index("ix_repuestos_x_ubicaciones_ubicacion_id", "ubicacion_id"),
    )

    repuesto_id: int = Field(primary_key=True, foreign_key="repuestos.id")
    ubicacion_id: int = Field(primary_key=True, foreign_key="ubicaciones.id")
    cantidad_fisica: int = Field(default=0, sa_column_kwargs={"server_default": text("0")})
    cantidad_reservada: int = Field(default=0, sa_column_kwargs={"server_default": text("0")})
    actualizado_en: datetime = Field(default_factory=fecha_actual, sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})
