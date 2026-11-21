"""Las claves no se versionan, son obligatorias y el error explica cómo definirlas."""

import tomllib
from pathlib import Path

import pytest

from autenticacion_jwt import validar_configuracion_jwt
from secretos import SecretoInvalidoError, clave_firma_auth
from utils import load_config, update_config

SECRET_KEY = "AUTOCONFIG_SECRETS__SECRET_KEY"
CLAVE_JWT = "AUTOCONFIG_SECRETS__CLAVE_JWT"


def test_config_toml_no_trae_claves():
    secretos = tomllib.loads(Path("config.toml").read_text(encoding="utf-8")).get("secrets", {})

    assert secretos == {}


def test_clave_ausente_advierte_y_falla_al_usarla(monkeypatch):
    from unittest.mock import Mock
    logger = Mock()
    monkeypatch.setattr("utils.get_logger", lambda: logger)
    monkeypatch.delenv(SECRET_KEY, raising=False)
    monkeypatch.delenv("AUTOCONFIG_SECRETS__AUTH_SIGNING_KEY", raising=False)
    config = load_config("default", reload=True)
    assert "Falta configurar AUTH_SIGNING_KEY" in str(logger.warning.call_args)
    with pytest.raises(SecretoInvalidoError, match="Falta configurar AUTH_SIGNING_KEY"):
        clave_firma_auth(config)


def test_clave_corta_advierte_y_falla_al_usarla(monkeypatch):
    from unittest.mock import Mock
    logger = Mock()
    monkeypatch.setattr("utils.get_logger", lambda: logger)
    monkeypatch.delenv(SECRET_KEY, raising=False)
    monkeypatch.setenv("AUTOCONFIG_SECRETS__AUTH_SIGNING_KEY", "123456")
    config = load_config("default", reload=True)
    assert "6 bytes" in str(logger.warning.call_args)
    with pytest.raises(SecretoInvalidoError, match="6 bytes") as error:
        clave_firma_auth(config)
    assert "123456" not in str(error.value)


def test_nombre_anterior_sigue_funcionando(monkeypatch):
    from unittest.mock import Mock
    logger = Mock()
    monkeypatch.setattr("utils.get_logger", lambda: logger)
    monkeypatch.delenv("AUTOCONFIG_SECRETS__AUTH_SIGNING_KEY", raising=False)
    monkeypatch.setenv(SECRET_KEY, "s" * 32)
    assert clave_firma_auth(load_config("default", reload=True)) == "s" * 32
    assert "obsoleta" in str(logger.warning.call_args)


def test_nombres_distintos_no_se_usan_silenciosamente(monkeypatch):
    monkeypatch.setenv(SECRET_KEY, "a" * 32)
    monkeypatch.setenv("AUTOCONFIG_SECRETS__AUTH_SIGNING_KEY", "b" * 32)
    config = load_config("default", reload=True)
    with pytest.raises(SecretoInvalidoError, match="valores distintos"):
        clave_firma_auth(config)


def test_servicio_valida_solo_al_firmar(monkeypatch):
    from services.auth_service import AuthService
    monkeypatch.delenv(SECRET_KEY, raising=False)
    monkeypatch.delenv("AUTOCONFIG_SECRETS__AUTH_SIGNING_KEY", raising=False)
    load_config("default", reload=True)
    servicio = AuthService()
    with pytest.raises(SecretoInvalidoError, match="AUTH_SIGNING_KEY"):
        servicio.create_token("usuario")
    with pytest.raises(SecretoInvalidoError, match="AUTH_SIGNING_KEY"):
        servicio.create_oauth_state()


def test_oauth_habilitado_exige_clave_al_crear_app(monkeypatch):
    from app import create_app

    monkeypatch.delenv(SECRET_KEY, raising=False)
    monkeypatch.delenv("AUTOCONFIG_SECRETS__AUTH_SIGNING_KEY", raising=False)
    base = load_config("default", reload=True)
    oauth = base.auth.OAUTH.model_copy(update={"ENABLED": True})
    config = update_config({"auth": base.auth.model_copy(update={"ENABLED": True, "OAUTH": oauth})})
    with pytest.raises(SecretoInvalidoError, match="AUTH_SIGNING_KEY"):
        create_app(cfg=config)


def configuracion_jwt(algoritmo: str, largo_clave: int):
    base = load_config("default", reload=True)
    jwt = base.auth.JWT.model_copy(update={"HABILITADO": True, "ALGORITMO": algoritmo})
    return update_config(
        {
            "auth": base.auth.model_copy(update={"JWT": jwt}),
            "secrets": {"CLAVE_JWT": "x" * largo_clave},
        }
    )


@pytest.mark.parametrize(
    ("algoritmo", "minimo"), [("HS256", 32), ("HS384", 48), ("HS512", 64)]
)
def test_la_clave_jwt_exige_el_largo_del_algoritmo(algoritmo, minimo):
    validar_configuracion_jwt(configuracion_jwt(algoritmo, minimo))

    with pytest.raises(ValueError, match=f"{minimo} bytes") as error:
        validar_configuracion_jwt(configuracion_jwt(algoritmo, minimo - 1))

    assert CLAVE_JWT in str(error.value)


def test_con_jwt_habilitado_la_clave_jwt_no_puede_faltar():
    with pytest.raises(ValueError, match="tiene 0 bytes") as error:
        validar_configuracion_jwt(configuracion_jwt("HS256", 0))

    assert CLAVE_JWT in str(error.value)
