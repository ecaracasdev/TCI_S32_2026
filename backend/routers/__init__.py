from .auth_router import router as auth_router
from .autenticacion_router import router as autenticacion_router
from .base_router import base_router

routers = [base_router, auth_router, autenticacion_router]
__all__ = ["routers"]
