"""Reglas de las claves secretas y los mensajes que explican cómo configurarlas.

Las claves no se versionan: se leen de variables de entorno (ver README, "Claves y
variables de entorno"). Este módulo concentra el largo mínimo y el texto de ayuda para
que el arranque y la validación del JWT expliquen lo mismo.
"""

from __future__ import annotations

from config import Config

LARGO_MINIMO_BYTES = 32

COMANDO_GENERAR = 'python3 -c "import secrets; print(secrets.token_urlsafe(48))"'


class SecretoInvalidoError(ValueError):
    """Una clave secreta falta o no cumple el largo mínimo."""


def variable_de_entorno(clave: str) -> str:
    """Nombre de la variable de entorno que define ``secrets.<clave>``."""

    return f"AUTOCONFIG_SECRETS__{clave}"


def como_definir(clave: str, largo_minimo: int = LARGO_MINIMO_BYTES) -> str:
    """Indica dónde se define una clave y cómo generar un valor válido."""

    return (
        f"Definila con la variable de entorno {variable_de_entorno(clave)} "
        f"(con Docker, en el archivo .env: copiá .env.example y completalo). "
        f"Necesita al menos {largo_minimo} bytes; para generar una: {COMANDO_GENERAR}"
    )


def clave_firma_auth(configuracion: Config) -> str:
    """Obtiene la clave de firmas de auth y la valida antes de utilizarla.

    El nombre anterior se acepta para no invalidar sesiones existentes.
    """
    actual = configuracion.secrets.AUTH_SIGNING_KEY
    anterior = configuracion.secrets.SECRET_KEY
    if actual.strip() and anterior.strip() and actual != anterior:
        raise SecretoInvalidoError("AUTH_SIGNING_KEY y SECRET_KEY contienen valores distintos; usá solo AUTH_SIGNING_KEY.")
    valor = actual if actual.strip() else anterior
    if not valor.strip():
        raise SecretoInvalidoError(f"Falta configurar AUTH_SIGNING_KEY. {como_definir('AUTH_SIGNING_KEY')}")

    largo = len(valor.encode("utf-8"))
    if largo < LARGO_MINIMO_BYTES:
        raise SecretoInvalidoError(
            f"AUTH_SIGNING_KEY tiene {largo} bytes y se exigen al menos {LARGO_MINIMO_BYTES}. "
            f"{como_definir('AUTH_SIGNING_KEY')}"
        )
    return valor
