"""Entidad persistida de usuario."""

from sqlalchemy import Boolean, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_db import Base


class UsuarioDb(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column("name", String(100), nullable=False)
    apellido: Mapped[str] = mapped_column("lastname", String(100), nullable=False)
    genero: Mapped[str] = mapped_column("gender", String(1), nullable=False)
    correo: Mapped[str] = mapped_column(
        "email", String(255), nullable=False, unique=True, index=True
    )
    hash_contrasena: Mapped[str] = mapped_column(
        "hashed_password", String(255), nullable=False
    )
    verificado: Mapped[bool] = mapped_column(
        "verified", Boolean, nullable=False, default=False, server_default=text("false")
    )
    roles: Mapped[list["RolDb"]] = relationship(
        secondary="usuarios_x_roles",
        back_populates="usuarios",
        lazy="selectin",
    )
