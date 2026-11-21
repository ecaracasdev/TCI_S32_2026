"""Pruebas del listado de roles sobre una base aislada."""

import sqlite3

from typer.testing import CliRunner

import listar_roles
from test_datos_prueba import _configurar


def test_lista_roles_incluso_sin_usuarios(tmp_path, monkeypatch):
    monkeypatch.delenv("AUTOCONFIG_SECRETS__SECRET_KEY", raising=False)
    monkeypatch.delenv("AUTOCONFIG_SECRETS__AUTH_SIGNING_KEY", raising=False)
    config, base = _configurar(tmp_path)
    with sqlite3.connect(base) as db:
        db.execute("CREATE TABLE roles (id INTEGER PRIMARY KEY, nombre TEXT UNIQUE, descripcion TEXT)")
        db.executemany("INSERT INTO roles VALUES (?, ?, ?)", [(1, "operario", "Operaciones"), (2, "sin_usuario", None)])
    cargar = listar_roles.load_config
    entornos = []

    def cargar_config(nombre, reload):
        entornos.append(nombre)
        return cargar(config, reload=reload)

    monkeypatch.setattr(listar_roles, "load_config", cargar_config)
    resultado = CliRunner().invoke(listar_roles.aplicacion, ["-c", "dev"])
    assert resultado.exit_code == 0, resultado.output
    assert entornos == ["dev"]
    assert "operario" in resultado.output
    assert "Operaciones" in resultado.output
    assert "sin_usuario" in resultado.output
    with sqlite3.connect(base) as db:
        assert db.execute("SELECT count(*) FROM roles").fetchone()[0] == 2
        assert db.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall() == [("roles",)]


def test_lista_vacia(tmp_path, monkeypatch):
    config, base = _configurar(tmp_path)
    with sqlite3.connect(base) as db:
        db.execute("CREATE TABLE roles (id INTEGER PRIMARY KEY, nombre TEXT UNIQUE, descripcion TEXT)")
    cargar = listar_roles.load_config
    monkeypatch.setattr(listar_roles, "load_config", lambda nombre, reload: cargar(config, reload=reload))
    resultado = CliRunner().invoke(listar_roles.aplicacion, [])
    assert resultado.exit_code == 0, resultado.output
    assert "No hay roles registrados" in resultado.output
