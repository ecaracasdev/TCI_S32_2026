"""Pruebas del listado de usuarios sobre una base aislada."""

import sqlite3

from typer.testing import CliRunner

import listar_usuarios
from test_datos_prueba import _cargar, _configurar


def test_lista_roles_y_usuarios_sin_roles(tmp_path, monkeypatch):
    monkeypatch.delenv("AUTOCONFIG_SECRETS__SECRET_KEY", raising=False)
    monkeypatch.delenv("AUTOCONFIG_SECRETS__AUTH_SIGNING_KEY", raising=False)
    config, base = _configurar(tmp_path)
    resultado = _cargar(config)
    assert resultado.exit_code == 0, resultado.output
    with sqlite3.connect(base) as db:
        db.execute("DELETE FROM usuarios_x_roles WHERE usuario_id = (SELECT id FROM usuarios WHERE correo = ?)", ("operario@test",))
    cargar = listar_usuarios.load_config
    entornos = []

    def cargar_config(nombre, reload):
        entornos.append(nombre)
        return cargar(config, reload=reload)

    monkeypatch.setattr(listar_usuarios, "load_config", cargar_config)
    respuesta = CliRunner().invoke(listar_usuarios.aplicacion, ["-c", "dev"])
    assert respuesta.exit_code == 0, respuesta.output
    assert entornos == ["dev"]
    assert "operario@test" in respuesta.output
    assert "Sin roles" in respuesta.output
    assert "empleado_mantenimiento" in respuesta.output
