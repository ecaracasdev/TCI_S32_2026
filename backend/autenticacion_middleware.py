"""Middleware de autenticación Bearer para JWT locales."""

from __future__ import annotations

import re

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from autenticacion_jwt import (
    TokenInvalidoError,
    validar_configuracion_jwt,
    validar_token_jwt,
)
from config import Config


class AutenticacionJWTMiddleware(BaseHTTPMiddleware):
    """Valida JWT en las rutas protegidas y guarda el ID autenticado."""

    def __init__(self, app, configuracion: Config):
        super().__init__(app)
        validar_configuracion_jwt(configuracion)
        self.configuracion = configuracion
        self.rutas_excluidas = [
            re.compile(patron) for patron in configuracion.auth.JWT.RUTAS_EXCLUIDAS
        ]

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if request.method == "OPTIONS" or any(
            patron.search(request.url.path) for patron in self.rutas_excluidas
        ):
            return await call_next(request)

        autorizacion = request.headers.get("Authorization", "")
        esquema, separador, token = autorizacion.partition(" ")
        if not separador or esquema.lower() != "bearer" or not token.strip():
            return self._no_autorizado()

        try:
            claims = validar_token_jwt(self.configuracion, token.strip())
            request.state.usuario_id = int(claims["sub"])
        except (TokenInvalidoError, KeyError, TypeError, ValueError):
            return self._no_autorizado()

        return await call_next(request)

    @staticmethod
    def _no_autorizado() -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": "Se requiere un token Bearer válido."},
            headers={"WWW-Authenticate": "Bearer"},
        )
