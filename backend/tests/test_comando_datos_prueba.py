"""Comprueba la ejecución del comando de datos de prueba como proceso independiente."""

import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from uuid import uuid4

import pytest


@pytest.mark.parametrize("atajo", [False, True], ids=["script", "atajo"])
@pytest.mark.parametrize("opcion_config", ["--config", "-c"])
def test_comando_crea_base(tmp_path, atajo, opcion_config):
    backend = Path(__file__).resolve().parents[1]
    entorno = f"prueba_cli_{uuid4().hex}"
    archivo_config = backend / f"config.{entorno}.toml"
    base = tmp_path / "dummy.sqlite3"
    plantilla = (backend / "config.toml").read_text(encoding="utf-8")
    linea_original = 'DB_NAME = "data/db.sqlite3"'
    assert plantilla.count(linea_original) == 1
    if 'SECRET_KEY = "123456"' in plantilla:
        plantilla = plantilla.replace('SECRET_KEY = "123456"', 'SECRET_KEY = "clave-temporal-de-prueba-0123456789"')
    else:
        plantilla = plantilla.replace("[secrets]", '[secrets]\nSECRET_KEY = "clave-temporal-de-prueba-0123456789"')
    archivo_config.write_text(
        plantilla.replace(linea_original, f'DB_NAME = "{base.as_posix()}"'),
        encoding="utf-8",
    )
    variables = os.environ.copy()
    variables.pop("AUTOCONFIG_SECRETS__SECRET_KEY", None)
    try:
        ejecutable = Path(sys.executable).parent / (
            "crear-dummy-db.exe" if os.name == "nt" else "crear-dummy-db"
        )
        comando = [str(ejecutable)] if atajo else [sys.executable, "datos_prueba.py"]
        resultado = subprocess.run(
            [*comando, opcion_config, entorno],
            cwd=backend,
            env=variables,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        assert resultado.returncode == 0, resultado.stderr + resultado.stdout
        with sqlite3.connect(base) as conexion:
            assert conexion.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert conexion.execute("PRAGMA foreign_key_check").fetchall() == []
            assert conexion.execute("SELECT count(*) FROM maquinas").fetchone()[0] == 18
            assert conexion.execute("SELECT count(*) FROM usuarios").fetchone()[0] == 5
    finally:
        archivo_config.unlink(missing_ok=True)
