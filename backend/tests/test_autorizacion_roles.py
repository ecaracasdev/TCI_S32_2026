"""Pruebas de las utilidades puras para autorización RBAC."""

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from autorizacion_roles import (
    requiere_atributo,
    requiere_rol,
    usuario_tiene_algun_rol,
    usuario_tiene_atributo,
    usuario_tiene_rol,
    usuario_tiene_todos_los_roles,
)


def crear_usuario(*roles: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=7,
        nombre="Ana",
        apellido="Pérez",
        correo="ana@example.test",
        verificado=True,
        roles=[SimpleNamespace(nombre=rol) for rol in roles],
    )


def test_consultas_de_roles_y_atributos():
    usuario = crear_usuario("empleado_mantenimiento", "encargado_mantenimiento")

    assert usuario_tiene_rol(usuario, "empleado_mantenimiento")
    assert usuario_tiene_algun_rol(usuario, "operario_maquina", "encargado_mantenimiento")
    assert usuario_tiene_todos_los_roles(
        usuario,
        "empleado_mantenimiento",
        "encargado_mantenimiento",
    )
    assert not usuario_tiene_todos_los_roles(usuario, "gerencia_administracion")
    assert usuario_tiene_atributo(usuario, "verificado", True)
    assert not usuario_tiene_atributo(usuario, "hash_contrasena", "secreto")
    assert not usuario_tiene_rol(None, "empleado_mantenimiento")


def test_dependencia_requiere_rol_y_acepta_coincidencia_configurada():
    usuario = crear_usuario("empleado_mantenimiento")
    dependencia_algun_rol = requiere_rol(
        "operario_maquina",
        "empleado_mantenimiento",
    )
    dependencia_todos_los_roles = requiere_rol(
        "operario_maquina",
        "empleado_mantenimiento",
        coincidencia="todos",
    )

    assert asyncio.run(dependencia_algun_rol(usuario=usuario)) is usuario
    with pytest.raises(HTTPException) as error:
        asyncio.run(dependencia_todos_los_roles(usuario=usuario))
    assert error.value.status_code == 403


def test_dependencia_requiere_atributo():
    usuario = crear_usuario("encargado_mantenimiento")
    dependencia = requiere_atributo("verificado", True)

    assert asyncio.run(dependencia(usuario=usuario)) is usuario
    with pytest.raises(HTTPException) as error:
        asyncio.run(requiere_atributo("correo", "otra@example.test")(usuario=usuario))
    assert error.value.status_code == 403


def test_no_se_permiten_atributos_sensibles_como_condicion():
    with pytest.raises(ValueError):
        requiere_atributo("hash_contrasena", "cualquier valor")
