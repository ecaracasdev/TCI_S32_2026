from datetime import datetime

from sqlalchemy import CheckConstraint, Index, Text, text
from sqlmodel import Field, SQLModel

from .fechas import fecha_actual


class MovimientoStockDb(SQLModel, table=True):
    __tablename__ = "movimientos_stock"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="movimientos_stock_cantidad_positiva"),
        Index("ix_movimientos_stock_repuesto_id_ocurrido_en", "repuesto_id", "ocurrido_en"),
        Index("ix_movimientos_stock_tipo_movimiento", "tipo_movimiento"),
        Index("ix_movimientos_stock_item_recepcion_compra_id", "item_recepcion_compra_id"),
        Index("ix_movimientos_stock_uso_repuesto_reparacion_id", "uso_repuesto_reparacion_id"),
        Index("ix_movimientos_stock_item_reserva_id", "item_reserva_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    repuesto_id: int = Field(foreign_key="repuestos.id")
    ubicacion_id: int = Field(foreign_key="ubicaciones.id")
    tipo_movimiento: str = Field(max_length=30)
    cantidad: int
    variacion_fisica: int
    variacion_reservada: int
    realizado_por_usuario_id: int = Field(foreign_key="usuarios.id")
    ocurrido_en: datetime = Field(default_factory=fecha_actual, sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})
    motivo: str | None = Field(default=None, sa_type=Text)
    item_recepcion_compra_id: int | None = Field(default=None, foreign_key="items_recepcion_compra.id")
    uso_repuesto_reparacion_id: int | None = Field(default=None, foreign_key="usos_repuestos_reparacion.id")
    item_reserva_id: int | None = Field(default=None, foreign_key="items_reserva.id")
