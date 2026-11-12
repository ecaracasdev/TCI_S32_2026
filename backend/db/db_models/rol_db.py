"""Entidad persistida de rol."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_db import Base


class RolDb(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(
        "rolename", String(100), nullable=False, unique=True, index=True
    )
    descripcion: Mapped[str | None] = mapped_column(
        "description", String(255), nullable=True
    )
    usuarios: Mapped[list["UsuarioDb"]] = relationship(
        secondary="usuarios_x_roles",
        back_populates="roles",
        lazy="selectin",
    )
