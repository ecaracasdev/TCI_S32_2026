"""DTOs del módulo local de autenticación y autorización."""

from pydantic import BaseModel, Field


class UsuarioCrearDto(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    genero: str = Field(min_length=1, max_length=1)
    correo: str = Field(min_length=3, max_length=255)
    contrasena: str = Field(min_length=8, max_length=1024)
    roles: list[str] = Field(default_factory=list)


class RolCrearDto(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=255)


class TokenAccesoDto(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UsuarioAutenticadoDto(BaseModel):
    usuario_id: int
    nombre: str
    apellido: str
    correo: str
    roles: list[str]
