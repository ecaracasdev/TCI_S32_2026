from datetime import datetime

from sqlalchemy import CheckConstraint, Index, Text, UniqueConstraint, text
from sqlmodel import Field, SQLModel

from .fechas import fecha_actual


class ReservaDb(SQLModel, table=True):
    __tablename__ = "reservas"

    id: int | None = Field(default=None, primary_key=True)
    creada_por_usuario_id: int = Field(foreign_key="usuarios.id")
    titulo: str = Field(max_length=200)
    motivo: str | None = Field(default=None, sa_type=Text)
    planificada_para: datetime
    estado: str = Field(max_length=50, default='planificada', sa_column_kwargs={"server_default": text("'planificada'")})
    autorizada_por_usuario_id: int | None = Field(default=None, foreign_key="usuarios.id")
    liberada_por_usuario_id: int | None = Field(default=None, foreign_key="usuarios.id")
    creada_en: datetime = Field(default_factory=fecha_actual, sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})
    liberada_en: datetime | None = Field(default=None)
    ejecutada_en: datetime | None = Field(default=None)


class ItemReservaDb(SQLModel, table=True):
    __tablename__ = "items_reserva"
    __table_args__ = (
        CheckConstraint("cantidad >= 1", name="items_reserva_cantidad_positiva"),
        CheckConstraint("cantidad_consumida >= 0", name="items_reserva_consumido_no_negativo"),
        CheckConstraint("cantidad_consumida <= cantidad", name="items_reserva_consumido_dentro_cantidad"),
        UniqueConstraint("reserva_id", "repuesto_id", "ubicacion_id"),
        Index("ix_items_reserva_repuesto_id", "repuesto_id"),
        Index("ix_items_reserva_ubicacion_id", "ubicacion_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    reserva_id: int = Field(foreign_key="reservas.id")
    repuesto_id: int = Field(foreign_key="repuestos.id")
    ubicacion_id: int = Field(foreign_key="ubicaciones.id")
    cantidad: int
    cantidad_consumida: int = Field(default=0, sa_column_kwargs={"server_default": text("0")})
