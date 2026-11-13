from datetime import datetime

from sqlalchemy import CheckConstraint, Index, Text, UniqueConstraint, text
from sqlmodel import Field, SQLModel

from .fechas import fecha_actual


class IncidenciaDb(SQLModel, table=True):
    __tablename__ = "incidencias"
    __table_args__ = (
        CheckConstraint("turno IN ('manana', 'tarde', 'noche')", name="incidencias_turno_valido"),
    )

    id: int | None = Field(default=None, primary_key=True)
    maquina_id: int = Field(foreign_key="maquinas.id")
    reportada_por_usuario_id: int = Field(foreign_key="usuarios.id")
    descripcion: str = Field(sa_type=Text)
    estado: str = Field(max_length=50, default='reportada', sa_column_kwargs={"server_default": text("'reportada'")})
    turno: str = Field(max_length=20)
    reportada_en: datetime = Field(default_factory=fecha_actual, sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})
    resuelta_en: datetime | None = Field(default=None)


class FotoIncidenciaDb(SQLModel, table=True):
    __tablename__ = "fotos_incidencias"

    id: int | None = Field(default=None, primary_key=True)
    incidencia_id: int = Field(foreign_key="incidencias.id")
    contenido_base64: str = Field(sa_type=Text)
    nombre_archivo: str | None = Field(default=None, max_length=255)
    tipo_mime: str = Field(max_length=100)
    capturada_en: datetime | None = Field(default=None)


class ReparacionDb(SQLModel, table=True):
    __tablename__ = "reparaciones"

    id: int | None = Field(default=None, primary_key=True)
    incidencia_id: int = Field(unique=True, foreign_key="incidencias.id")
    empleado_id: int | None = Field(default=None, foreign_key="usuarios.id")
    estado: str = Field(max_length=50, default='pendiente', sa_column_kwargs={"server_default": text("'pendiente'")})
    iniciada_en: datetime | None = Field(default=None)
    completada_en: datetime | None = Field(default=None)


class UsoRepuestoReparacionDb(SQLModel, table=True):
    __tablename__ = "usos_repuestos_reparacion"
    __table_args__ = (
        CheckConstraint("cantidad >= 1", name="usos_repuestos_reparacion_cantidad_positiva"),
        UniqueConstraint("reparacion_id", "repuesto_id"),
        Index("ix_usos_repuestos_reparacion_repuesto_id", "repuesto_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    reparacion_id: int = Field(foreign_key="reparaciones.id")
    repuesto_id: int = Field(foreign_key="repuestos.id")
    cantidad: int
    usada_por_usuario_id: int = Field(foreign_key="usuarios.id")
    usada_en: datetime = Field(default_factory=fecha_actual, sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})


class InformeResolucionDb(SQLModel, table=True):
    __tablename__ = "informes_resolucion"

    id: int | None = Field(default=None, primary_key=True)
    reparacion_id: int = Field(unique=True, foreign_key="reparaciones.id")
    empleado_id: int = Field(foreign_key="usuarios.id")
    resumen: str = Field(sa_type=Text)
    creada_en: datetime = Field(default_factory=fecha_actual, sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")})
