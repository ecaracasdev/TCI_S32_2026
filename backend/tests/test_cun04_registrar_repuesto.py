"""Pruebas de aceptación de CUN-04."""
import sqlite3
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from app import create_app
from autorizacion_roles import obtener_usuario_actual
from utils import load_config, update_config

@pytest.fixture
def catalogo(tmp_path):
    ruta = tmp_path / "cun04.sqlite3"
    config = load_config(reload=True)
    jwt = config.auth.JWT.model_copy(update={"HABILITADO": False})
    config = update_config({"database": {"DB_NAME": ruta.as_posix()}, "auth": config.auth.model_copy(update={"JWT": jwt})})
    app = create_app(cfg=config)
    app.dependency_overrides[obtener_usuario_actual] = lambda: SimpleNamespace(roles=[SimpleNamespace(nombre="encargado_mantenimiento")])
    with TestClient(app) as client:
        yield client, ruta

def datos():
    return {"codigo": "CUN04-001", "nombre": "Rodamiento", "descripcion": "Sellado", "stock_minimo": 3}

def estado(ruta):
    with sqlite3.connect(ruta) as db:
        return tuple(db.execute(f"SELECT count(*) FROM {tabla}").fetchone()[0] for tabla in ("repuestos", "repuestos_x_ubicaciones", "movimientos_stock"))

def test_cun04_registro_valido_sin_stock_ni_movimientos(catalogo):
    client, ruta = catalogo
    antes = estado(ruta)
    respuesta = client.post("/api/v0/repuestos", json=datos())
    assert respuesta.status_code == 201, respuesta.text
    repuesto = respuesta.json()
    assert repuesto["activo"] is True
    assert repuesto["stock"] == []
    assert [repuesto[k] for k in ("stock_fisico_total", "stock_reservado_total", "stock_disponible_total")] == [0, 0, 0]
    assert estado(ruta) == (antes[0] + 1, antes[1], antes[2])

def test_cun04_codigo_duplicado_no_modifica_catalogo(catalogo):
    client, ruta = catalogo
    assert client.post("/api/v0/repuestos", json=datos()).status_code == 201
    antes = estado(ruta)
    assert client.post("/api/v0/repuestos", json=datos()).status_code == 409
    assert estado(ruta) == antes

@pytest.mark.parametrize("cambios", [{"codigo": ""}, {"nombre": ""}, {"stock_minimo": -1}, {"stock_minimo": 1.5}])
def test_cun04_datos_invalidos_no_modifican_catalogo(catalogo, cambios):
    client, ruta = catalogo
    antes = estado(ruta)
    assert client.post("/api/v0/repuestos", json={**datos(), **cambios}).status_code == 422
    assert estado(ruta) == antes

@pytest.mark.parametrize("rol", ["operario_maquina", "empleado_mantenimiento", "gerencia_administracion"])
def test_cun04_roles_sin_permiso(catalogo, rol):
    client, ruta = catalogo
    client.app.dependency_overrides[obtener_usuario_actual] = lambda: SimpleNamespace(roles=[SimpleNamespace(nombre=rol)])
    antes = estado(ruta)
    assert client.post("/api/v0/repuestos", json=datos()).status_code == 403
    assert estado(ruta) == antes

@pytest.mark.parametrize("campo", ["codigo", "nombre", "stock_minimo"])
def test_cun04_dato_obligatorio_faltante(catalogo, campo):
    client, ruta = catalogo
    antes = estado(ruta)
    entrada = datos()
    del entrada[campo]
    assert client.post("/api/v0/repuestos", json=entrada).status_code == 422
    assert estado(ruta) == antes


def test_cun04_descripcion_opcional(catalogo):
    client, _ = catalogo
    entrada = datos()
    del entrada["descripcion"]
    respuesta = client.post("/api/v0/repuestos", json=entrada)
    assert respuesta.status_code == 201
    assert respuesta.json()["descripcion"] is None


def test_cun04_sin_token_no_modifica_catalogo(tmp_path):
    ruta = tmp_path / "cun04_seguridad.sqlite3"
    config = load_config(reload=True)
    jwt = config.auth.JWT.model_copy(update={"HABILITADO": True})
    config = update_config({
        "database": {"DB_NAME": ruta.as_posix()},
        "auth": config.auth.model_copy(update={"JWT": jwt}),
        "secrets": {"CLAVE_JWT": "x" * 64},
    })
    with TestClient(create_app(cfg=config)) as client:
        antes = estado(ruta)
        assert client.post("/api/v0/repuestos", json=datos()).status_code == 401
        assert estado(ruta) == antes
