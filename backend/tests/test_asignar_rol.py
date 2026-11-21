"""Pruebas del comando de asignación de roles sobre una base aislada."""

import sqlite3

import pytest
from typer.testing import CliRunner

import gestionar_acceso
from asignar_rol import aplicacion
from test_datos_prueba import _cargar, _configurar


@pytest.fixture
def catalogo(tmp_path, monkeypatch):
    config, base = _configurar(tmp_path)
    resultado = _cargar(config)
    assert resultado.exit_code == 0, resultado.output
    cargar = gestionar_acceso.load_config
    monkeypatch.setattr(gestionar_acceso, "load_config", lambda entorno, reload: cargar(config, reload=reload))
    return base


def roles(base, correo):
    with sqlite3.connect(base) as db:
        return db.execute(
            "SELECT r.nombre FROM roles r JOIN usuarios_x_roles ur ON ur.rol_id = r.id "
            "JOIN usuarios u ON u.id = ur.usuario_id WHERE u.correo = ? ORDER BY r.nombre",
            (correo,),
        ).fetchall()


def test_asigna_rol_por_correo_y_conserva_los_existentes(catalogo):
    args = ["--user", " EMPLEADO@TEST ", "--role", "gerencia_administracion", "-c", "dev"]
    resultado = CliRunner().invoke(aplicacion, args)
    assert resultado.exit_code == 0, resultado.output
    assert roles(catalogo, "empleado@test") == [("empleado_mantenimiento",), ("gerencia_administracion",)]
    repetido = CliRunner().invoke(aplicacion, args)
    assert repetido.exit_code == 0, repetido.output
    assert "ya tiene" in repetido.output
    assert len(roles(catalogo, "empleado@test")) == 2


@pytest.mark.parametrize("usuario,rol", [
    ("nadie@test", "empleado_mantenimiento"),
    ("empleado@test", "rol_inexistente"),
])
def test_usuario_o_rol_inexistente_no_cambia_asignaciones(catalogo, usuario, rol):
    antes = roles(catalogo, "empleado@test")
    resultado = CliRunner().invoke(aplicacion, ["--user", usuario, "--role", rol, "--config", "dev"])
    assert resultado.exit_code != 0
    assert "No existe" in resultado.output
    assert roles(catalogo, "empleado@test") == antes
