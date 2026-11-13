from sqlalchemy import Index, text
from sqlmodel import Field, SQLModel


class UsuarioDb(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    genero: str = Field(max_length=1)
    correo: str = Field(unique=True, max_length=255)
    hash_contrasena: str = Field(max_length=255)
    verificado: bool = Field(default=False, sa_column_kwargs={"server_default": text("false")})


class RolDb(SQLModel, table=True):
    __tablename__ = "roles"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, max_length=100)
    descripcion: str | None = Field(default=None, max_length=255)


class UsuarioXRolDb(SQLModel, table=True):
    __tablename__ = "usuarios_x_roles"
    __table_args__ = (
        Index("ix_usuarios_x_roles_rol_id", "rol_id"),
    )

    usuario_id: int = Field(primary_key=True, foreign_key="usuarios.id")
    rol_id: int = Field(primary_key=True, foreign_key="roles.id")
