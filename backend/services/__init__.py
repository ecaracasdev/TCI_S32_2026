from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from .auth_service import AuthService
from .autenticacion_service import ServicioAutenticacion
from .db_service import DbService

def get_auth_service() -> AuthService:
    return AuthService()

def get_db_service() -> DbService:
    return DbService()


def obtener_servicio_autenticacion(
    sesion: AsyncSession = Depends(get_db),
) -> ServicioAutenticacion:
    return ServicioAutenticacion(sesion)

__all__ = [
    "DbService",
    "AuthService",
    "ServicioAutenticacion",
    "obtener_servicio_autenticacion",
]
