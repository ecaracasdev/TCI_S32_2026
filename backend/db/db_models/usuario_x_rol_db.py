"""Tabla asociativa entre usuarios y roles."""

from sqlalchemy import Column, ForeignKey, Integer, Table

from .base_db import Base


usuarios_x_roles = Table(
    "usuarios_x_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)
