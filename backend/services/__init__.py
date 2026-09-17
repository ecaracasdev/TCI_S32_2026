from .db_service import DbService
from .auth_service import AuthService

def get_auth_service() -> AuthService:
    return AuthService()

def get_db_service() -> DbService:
    return DbService()

__all__ = [
    "DbService",
    "AuthService",
]
