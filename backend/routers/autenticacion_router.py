"""Rutas de inicio de sesión local y consulta de identidad."""

from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from autenticacion_jwt import crear_token_jwt
from autorizacion_roles import obtener_usuario_actual
from config import Config
from db.db_models.usuario_db import UsuarioDb
from models.autenticacion_mdl import (
    TokenAccesoDto,
    UsuarioAutenticadoDto,
)
from services import obtener_servicio_autenticacion
from services.autenticacion_service import ServicioAutenticacion
from utils import get_config


router = APIRouter(prefix="/auth", tags=["Autenticación local"])


TOKEN_HEADERS = {"Cache-Control": "no-store", "Pragma": "no-cache"}


@router.post(
    "/token",
    response_model=TokenAccesoDto,
    summary="Iniciar sesión local",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "required": ["grant_type", "username", "password"],
                        "properties": {
                            "grant_type": {"type": "string", "enum": ["password"]},
                            "username": {"type": "string", "description": "Correo del usuario"},
                            "password": {"type": "string", "format": "password"},
                        },
                    }
                }
            },
        }
    },
)
async def iniciar_sesion(
    request: Request,
    response: Response,
    servicio: ServicioAutenticacion = Depends(obtener_servicio_autenticacion),
) -> TokenAccesoDto | JSONResponse:
    """Valida correo y contraseña y devuelve un JWT de acceso."""

    configuracion: Config = get_config()
    if not configuracion.auth.ENABLED or not configuracion.auth.JWT.HABILITADO:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La autenticación JWT local no está habilitada.",
        )
    def error_token(codigo: str) -> JSONResponse:
        return JSONResponse({"error": codigo}, status_code=400, headers=TOKEN_HEADERS)

    tipo = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if tipo != "application/x-www-form-urlencoded":
        return error_token("invalid_request")

    cuerpo = bytearray()
    async for fragmento in request.stream():
        if len(cuerpo) + len(fragmento) > 16_384:
            return error_token("invalid_request")
        cuerpo.extend(fragmento)
    try:
        campos = parse_qs(
            cuerpo.decode("utf-8"), keep_blank_values=True, errors="strict",
            max_num_fields=32,
        )
    except ValueError:
        return error_token("invalid_request")
    if any(len(valores) != 1 for valores in campos.values()):
        return error_token("invalid_request")
    tipo_grant = campos.get("grant_type", [""])[0]
    if not tipo_grant:
        return error_token("invalid_request")
    if tipo_grant != "password":
        return error_token("unsupported_grant_type")
    correo = campos.get("username", [""])[0].strip()
    contrasena = campos.get("password", [""])[0]
    if not 3 <= len(correo) <= 255 or not 1 <= len(contrasena) <= 1024:
        return error_token("invalid_request")
    if campos.get("scope", [""])[0]:
        return error_token("invalid_scope")

    usuario = await servicio.autenticar(correo, contrasena)
    if usuario is None:
        return error_token("invalid_grant")
    token, duracion = crear_token_jwt(
        configuracion, usuario.id, roles=[rol.nombre for rol in usuario.roles]
    )
    response.headers.update(TOKEN_HEADERS)
    return TokenAccesoDto(access_token=token, expires_in=duracion)


@router.get(
    "/me",
    response_model=UsuarioAutenticadoDto,
    summary="Consultar el usuario autenticado",
)
async def consultar_usuario_actual(
    usuario: UsuarioDb = Depends(obtener_usuario_actual),
) -> UsuarioAutenticadoDto:
    """Devuelve los datos y roles vigentes del usuario autenticado."""

    return UsuarioAutenticadoDto(
        usuario_id=usuario.id,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        roles=[rol.nombre for rol in usuario.roles],
    )
