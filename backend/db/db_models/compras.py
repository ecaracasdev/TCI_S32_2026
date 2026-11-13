from datetime import datetime

from sqlalchemy import CheckConstraint, Index, Text, UniqueConstraint, text
from sqlmodel import Field, SQLModel

from .fechas import fecha_actual


class PedidoCompraDb(SQLModel, table=True):
    __tablename__ = "pedidos_compra"
    __table_args__ = (
        CheckConstraint("urgencia IN ('normal', 'urgente')", name="pedidos_compra_urgencia_valida"),
        CheckConstraint("origen IN ('manual', 'automatico')", name="pedidos_compra_origen_valido"),
        CheckConstraint("estado IN ('creado', 'pendiente_revision', 'pendiente_aprobacion', 'confirmado', 'cancelado', 'pendiente_recepcion', 'recibido')", name="pedidos_compra_estado_valido"),
    )

    id: int | None = Field(default=None, primary_key=True)
    creada_por_usuario_id: int = Field(foreign_key="usuarios.id")
    urgencia: str = Field(max_length=20, default='normal', sa_column_kwargs={"server_default": text("'normal'")})
    origen: str = Field(max_length=20, default='manual', sa_column_kwargs={"server_default": text("'manual'")})
    estado: str = Field(max_length=50, default='creado', sa_column_kwargs={"server_default": text("'creado'")})
    motivo: str | None = Field(default=None, sa_type=Text)
    asignado_a_usuario_id: int | None = Field(default=None, foreign_key="usuarios.id")
    revision_resuelta_por_usuario_id: int | None = Field(default=None, foreign_key="usuarios.id")
    revision_resuelta_en: datetime | None = Field(default=None)
    motivo_cancelacion: str | None = Field(default=None, sa_type=Text)
    creado_en: datetime = Field(default_factory=fecha_actual, sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})


class ItemPedidoCompraDb(SQLModel, table=True):
    __tablename__ = "items_pedido_compra"
    __table_args__ = (
        CheckConstraint("cantidad_solicitada >= 1", name="items_pedido_compra_cantidad_positiva"),
        UniqueConstraint("pedido_compra_id", "repuesto_id"),
        Index("ix_items_pedido_compra_repuesto_id", "repuesto_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    pedido_compra_id: int = Field(foreign_key="pedidos_compra.id")
    repuesto_id: int = Field(foreign_key="repuestos.id")
    cantidad_solicitada: int


class RecepcionCompraDb(SQLModel, table=True):
    __tablename__ = "recepciones_compra"

    id: int | None = Field(default=None, primary_key=True)
    pedido_compra_id: int = Field(foreign_key="pedidos_compra.id")
    recibida_por_usuario_id: int = Field(foreign_key="usuarios.id")
    delegada_a_usuario_id: int | None = Field(default=None, foreign_key="usuarios.id")
    recibida_en: datetime = Field(default_factory=fecha_actual, sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})
    notas: str | None = Field(default=None, sa_type=Text)


class ItemRecepcionCompraDb(SQLModel, table=True):
    __tablename__ = "items_recepcion_compra"
    __table_args__ = (
        CheckConstraint("cantidad >= 1", name="items_recepcion_compra_cantidad_positiva"),
        UniqueConstraint("recepcion_id", "item_pedido_compra_id", "ubicacion_id"),
        Index("ix_items_recepcion_compra_item_pedido_compra_id", "item_pedido_compra_id"),
        Index("ix_items_recepcion_compra_ubicacion_id", "ubicacion_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    recepcion_id: int = Field(foreign_key="recepciones_compra.id")
    item_pedido_compra_id: int = Field(foreign_key="items_pedido_compra.id")
    ubicacion_id: int = Field(foreign_key="ubicaciones.id")
    cantidad: int
