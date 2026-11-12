"""Firma, validación y hashing de credenciales para la autenticación local."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import time
from typing import Any

from jwcrypto import jwk, jwt
from jwcrypto.common import JWException, base64url_encode

from config import Config


ALGORITMOS_HMAC_COMPATIBLES = {"HS256", "HS384", "HS512"}
PARAMETROS_SCRYPT = {"n": 2**14, "r": 8, "p": 1}


class TokenInvalidoError(ValueError):
    """El token no es válido, expiró o no cumple los requisitos locales."""


def validar_configuracion_jwt(configuracion: Config) -> None:
    """Valida la configuración JWT antes de iniciar el servidor."""

    jwt_cfg = configuracion.auth.JWT
    if not jwt_cfg.HABILITADO:
        return
    if not configuracion.auth.ENABLED:
        raise ValueError("JWT local requiere auth.ENABLED = true.")
    if configuracion.auth.KEYCLOAK.ENABLED:
        raise ValueError("JWT local y Keycloak no pueden estar habilitados a la vez.")
    if jwt_cfg.DURACION_TOKEN_MINUTOS <= 0:
        raise ValueError("auth.JWT.DURACION_TOKEN_MINUTOS debe ser mayor que cero.")
    if not jwt_cfg.ALGORITMOS_PERMITIDOS:
        raise ValueError("auth.JWT.ALGORITMOS_PERMITIDOS no puede estar vacío.")
    algoritmos = set(jwt_cfg.ALGORITMOS_PERMITIDOS)
    no_soportados = algoritmos - ALGORITMOS_HMAC_COMPATIBLES
    if no_soportados:
        raise ValueError(
            "Algoritmos JWT no soportados: " + ", ".join(sorted(no_soportados))
        )
    if jwt_cfg.ALGORITMO not in algoritmos:
        raise ValueError("auth.JWT.ALGORITMO debe estar en ALGORITMOS_PERMITIDOS.")
    clave = configuracion.secrets.CLAVE_JWT.encode("utf-8")
    largo_minimo = {"HS256": 32, "HS384": 48, "HS512": 64}[jwt_cfg.ALGORITMO]
    if len(clave) < largo_minimo:
        raise ValueError(
            f"secrets.CLAVE_JWT debe tener al menos {largo_minimo} bytes para "
            f"{jwt_cfg.ALGORITMO}."
        )
    try:
        for patron in jwt_cfg.RUTAS_EXCLUIDAS:
            re.compile(patron)
    except re.error as error:
        raise ValueError(f"Patrón de ruta excluida inválido: {error}") from error


def _crear_clave(configuracion: Config) -> jwk.JWK:
    clave = configuracion.secrets.CLAVE_JWT.encode("utf-8")
    return jwk.JWK(kty="oct", k=base64url_encode(clave))


def crear_token_jwt(
    configuracion: Config, usuario_id: int, *, roles: list[str]
) -> tuple[str, int]:
    """Emite un JWT de acceso para un usuario identificado por su ID."""

    jwt_cfg = configuracion.auth.JWT
    duracion = jwt_cfg.DURACION_TOKEN_MINUTOS * 60
    ahora = int(time.time())
    token = jwt.JWT(
        header={"alg": jwt_cfg.ALGORITMO, "typ": "JWT"},
        claims={
            "iss": jwt_cfg.EMISOR,
            "sub": str(usuario_id),
            "aud": jwt_cfg.AUDIENCIA,
            "iat": ahora,
            "exp": ahora + duracion,
            "jti": secrets.token_urlsafe(24),
            "roles": roles,
        },
    )
    token.make_signed_token(_crear_clave(configuracion))
    return token.serialize(), duracion


def validar_token_jwt(configuracion: Config, token: str) -> dict[str, Any]:
    """Verifica firma, algoritmo y fechas; devuelve los claims validados."""

    jwt_cfg = configuracion.auth.JWT
    try:
        if not isinstance(token, str) or token.count(".") != 2:
            raise TokenInvalidoError("El token no usa serialización compacta.")
        token_validado = jwt.JWT(
            jwt=token,
            key=_crear_clave(configuracion),
            algs=[jwt_cfg.ALGORITMO],
            expected_type="JWS",
        )
        claims = json.loads(token_validado.claims)
        if not isinstance(claims, dict):
            raise TokenInvalidoError("El contenido del token no es válido.")
        if claims.get("iss") != jwt_cfg.EMISOR or claims.get("aud") != jwt_cfg.AUDIENCIA:
            raise TokenInvalidoError("El emisor o la audiencia no son válidos.")
        ahora = int(time.time())
        sujeto = claims.get("sub")
        if not isinstance(sujeto, str) or not sujeto.isdecimal():
            raise TokenInvalidoError("El token no contiene un sujeto válido.")
        if int(claims["exp"]) <= ahora:
            raise TokenInvalidoError("El token expiró.")
        if int(claims["iat"]) > ahora:
            raise TokenInvalidoError("La fecha de emisión del token no es válida.")
        return claims
    except (JWException, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise TokenInvalidoError("El token no es válido.") from error


def crear_hash_contrasena(contrasena: str) -> str:
    """Protege una contraseña con scrypt y un salt aleatorio."""

    sal = secrets.token_bytes(16)
    derivada = hashlib.scrypt(
        contrasena.encode("utf-8"),
        salt=sal,
        dklen=32,
        maxmem=64 * 1024 * 1024,
        **PARAMETROS_SCRYPT,
    )
    sal_texto = base64.urlsafe_b64encode(sal).decode("ascii").rstrip("=")
    hash_texto = base64.urlsafe_b64encode(derivada).decode("ascii").rstrip("=")
    return f"scrypt$16384$8$1${sal_texto}${hash_texto}"


def verificar_contrasena(contrasena: str, hash_almacenado: str) -> bool:
    """Compara una contraseña con un hash scrypt almacenado."""

    try:
        algoritmo, n, r, p, sal_texto, hash_texto = hash_almacenado.split("$", 5)
        if (algoritmo, n, r, p) != ("scrypt", "16384", "8", "1"):
            return False
        sal = base64.urlsafe_b64decode(sal_texto + "=" * (-len(sal_texto) % 4))
        esperado = base64.urlsafe_b64decode(
            hash_texto + "=" * (-len(hash_texto) % 4)
        )
        obtenido = hashlib.scrypt(
            contrasena.encode("utf-8"),
            salt=sal,
            dklen=len(esperado),
            maxmem=64 * 1024 * 1024,
            **PARAMETROS_SCRYPT,
        )
        return hmac.compare_digest(obtenido, esperado)
    except (ValueError, TypeError):
        return False
