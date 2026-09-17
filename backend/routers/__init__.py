from .auth_router import router as auth_router
from .base_router import base_router

routers = [base_router, auth_router]
__all__ = ["routers"]
