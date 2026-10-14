from enum import Enum

from pydantic import Field

from .common_mdl import ResponseDto


class RolUsuario(str, Enum):
    """Roles de aplicación definidos por el dominio del TCI."""

    OPERARIO_MAQUINA = "operario_maquina"
    EMPLEADO_MANTENIMIENTO = "empleado_mantenimiento"
    ENCARGADO_MANTENIMIENTO = "encargado_mantenimiento"
    GERENCIA_ADMINISTRACION = "gerencia_administracion"


class AuthUserResponseDto(ResponseDto):
    """Identidad y roles de la persona autenticada en el contrato v0."""

    user_id: str = Field(description="Identificador de la persona autenticada.")
    username: str = Field(description="Nombre de usuario para mostrar.")
    roles: list[RolUsuario] = Field(
        description="Roles de aplicación asignados a la persona autenticada.",
        examples=[
            [
                "operario_maquina",
                "empleado_mantenimiento",
                "encargado_mantenimiento",
                "gerencia_administracion",
            ]
        ],
    )
