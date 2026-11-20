"""Pruebas del CUN-01: tomar una incidencia, registrar repuestos usados (RN-01) y resolverla.

Cada prueba arma sus propios datos para no depender del script de datos de prueba.
"""

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import create_app
from autenticacion_jwt import crear_hash_contrasena
from utils import load_config, update_config

CONTRASENA = "Prueba1234"
ROLES = {
    "operario": "operario_maquina",
    "empleado": "empleado_mantenimiento",
    "encargado": "encargado_mantenimiento",
    "gerencia": "gerencia_administracion",
}
# (id, estado) de las incidencias de la prueba, todas sobre la máquina 1.
INCIDENCIAS = [(1, "reportada"), (2, "en_triage"), (3, "resuelta")]
# (id, código, mínimo)
REPUESTOS = [(1, "REP-1", 5), (2, "REP-2", 1), (3, "REP-3", 0)]
# (repuesto, ubicación, físico, reservado). El repuesto 2 tiene 3 de sus 4 unidades reservadas.
EXISTENCIAS = [(1, 1, 5, 0), (1, 2, 3, 0), (2, 1, 4, 3)]


def cargar_datos(base: Path) -> None:
    with sqlite3.connect(base) as db:
        for numero, (nombre, rol) in enumerate(ROLES.items(), start=1):
            db.execute("INSERT INTO roles (id, nombre) VALUES (?, ?)", (numero, rol))
            db.execute(
                "INSERT INTO usuarios (id, nombre, apellido, genero, correo, hash_contrasena, verificado)"
                " VALUES (?, ?, 'Prueba', 'F', ?, ?, 1)",
                (numero, nombre.title(), f"{nombre}@demo.invalid", crear_hash_contrasena(CONTRASENA)),
            )
            db.execute("INSERT INTO usuarios_x_roles (usuario_id, rol_id) VALUES (?, ?)", (numero, numero))
        db.execute("INSERT INTO tipos_maquina (id, nombre) VALUES (1, 'Prensa')")
        db.execute("INSERT INTO maquinas (id, codigo, tipo_maquina_id) VALUES (1, 'P-01', 1)")
        db.executemany(
            "INSERT INTO incidencias (id, maquina_id, reportada_por_usuario_id, descripcion, estado, turno)"
            " VALUES (?, 1, 1, 'Pierde aceite.', ?, 'tarde')",
            INCIDENCIAS,
        )
        db.executemany("INSERT INTO ubicaciones (id, codigo) VALUES (?, ?)", [(1, "A-01"), (2, "B-02")])
        db.executemany(
            "INSERT INTO repuestos (id, codigo, nombre, stock_minimo) VALUES (?, ?, ?, ?)",
            [(i, codigo, f"Repuesto {i}", minimo) for i, codigo, minimo in REPUESTOS],
        )
        db.executemany(
            "INSERT INTO repuestos_x_ubicaciones (repuesto_id, ubicacion_id, cantidad_fisica, cantidad_reservada)"
            " VALUES (?, ?, ?, ?)",
            EXISTENCIAS,
        )


@pytest.fixture
def entorno(tmp_path: Path):
    base = tmp_path / "reparaciones.sqlite3"
    configuracion = load_config(reload=True)
    jwt = configuracion.auth.JWT.model_copy(update={"HABILITADO": True})
    app = create_app(
        cfg=update_config(
            {
                "database": {"DB_NAME": base.as_posix()},
                "auth": configuracion.auth.model_copy(update={"JWT": jwt}),
                "secrets": {"CLAVE_JWT": "x" * 64},
            }
        )
    )
    with TestClient(app) as client:
        cargar_datos(base)
        yield client, base
    load_config(reload=True)


def sesion(client: TestClient, nombre: str) -> dict:
    respuesta = client.post(
        "/auth/token",
        data={"username": f"{nombre}@demo.invalid", "password": CONTRASENA, "grant_type": "password"},
    )
    assert respuesta.status_code == 200, respuesta.text
    return {"Authorization": f"Bearer {respuesta.json()['access_token']}"}


def existencia(base: Path, repuesto_id: int, ubicacion_id: int) -> tuple[int, int]:
    """(físico, reservado) de una existencia."""
    with sqlite3.connect(base) as db:
        return db.execute(
            "SELECT cantidad_fisica, cantidad_reservada FROM repuestos_x_ubicaciones"
            " WHERE repuesto_id = ? AND ubicacion_id = ?",
            (repuesto_id, ubicacion_id),
        ).fetchone()


def consultar(base: Path, sql: str, *parametros):
    with sqlite3.connect(base) as db:
        return db.execute(sql, parametros).fetchall()


def tomar(client: TestClient, empleado: dict, incidencia_id: int = 1) -> dict:
    respuesta = client.post(f"/api/v0/incidencias/{incidencia_id}/reparacion", headers=empleado)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_cun01_tomar_registrar_usos_y_resolver(entorno):
    client, base = entorno
    empleado = sesion(client, "empleado")

    reparacion = tomar(client, empleado)
    assert (reparacion["estado"], reparacion["empleado_id"], reparacion["usos"]) == ("en_curso", 2, [])
    incidencia = client.get("/api/v0/incidencias/1", headers=empleado).json()
    assert (incidencia["estado"], incidencia["reparacion_id"]) == ("en_reparacion", reparacion["id"])

    # Sin ubicación indicada, descuenta de la que tiene más disponible (A-01, con 5).
    uso = client.post(
        f"/api/v0/reparaciones/{reparacion['id']}/usos", headers=empleado, json={"repuesto_id": 1, "cantidad": 2}
    )
    assert uso.status_code == 201, uso.text
    assert (uso.json()["repuesto"]["codigo"], uso.json()["cantidad"], uso.json()["usada_por_usuario_id"]) == ("REP-1", 2, 2)
    assert existencia(base, 1, 1) == (3, 0)
    # El mismo repuesto, indicando la ubicación: se suma a la misma línea.
    otra = client.post(
        f"/api/v0/reparaciones/{reparacion['id']}/usos",
        headers=empleado,
        json={"repuesto_id": 1, "cantidad": 1, "ubicacion_id": 2},
    )
    assert otra.status_code == 201, otra.text
    assert otra.json()["cantidad"] == 3
    assert existencia(base, 1, 2) == (2, 0)
    # Cada uso deja su movimiento de consumo, enlazado a la línea (RN-06).
    assert consultar(
        base,
        "SELECT ubicacion_id, cantidad, variacion_fisica, variacion_reservada FROM movimientos_stock"
        " WHERE tipo_movimiento = 'consumo' AND uso_repuesto_reparacion_id = ? ORDER BY id",
        uso.json()["id"],
    ) == [(1, 2, -2, 0), (2, 1, -1, 0)]

    detalle = client.get(f"/api/v0/reparaciones/{reparacion['id']}", headers=empleado).json()
    assert [(u["repuesto"]["codigo"], u["cantidad"]) for u in detalle["usos"]] == [("REP-1", 3)]
    assert detalle["informe_resolucion"] is None

    informe = client.post(
        f"/api/v0/reparaciones/{reparacion['id']}/informe",
        headers=empleado,
        json={"resumen": "Se cambió el retén y se repuso el aceite."},
    )
    assert informe.status_code == 201, informe.text
    assert informe.json()["resumen"] == "Se cambió el retén y se repuso el aceite."
    incidencia = client.get("/api/v0/incidencias/1", headers=empleado).json()
    assert incidencia["estado"] == "resuelta"
    assert incidencia["resuelta_en"] is not None
    detalle = client.get(f"/api/v0/reparaciones/{reparacion['id']}", headers=empleado).json()
    assert detalle["estado"] == "completada"
    assert detalle["completada_en"] is not None
    assert detalle["informe_resolucion"]["id"] == informe.json()["id"]

    # Una reparación terminada ya no admite usos ni otro informe, y el stock no cambia.
    tarde = client.post(
        f"/api/v0/reparaciones/{reparacion['id']}/usos", headers=empleado, json={"repuesto_id": 1, "cantidad": 1}
    )
    assert (tarde.status_code, tarde.json()["codigo"]) == (409, "reparacion_no_en_curso")
    otro_informe = client.post(
        f"/api/v0/reparaciones/{reparacion['id']}/informe", headers=empleado, json={"resumen": "Otra vez."}
    )
    assert (otro_informe.status_code, otro_informe.json()["codigo"]) == (409, "reparacion_no_en_curso")
    assert (existencia(base, 1, 1), existencia(base, 1, 2)) == ((3, 0), (2, 0))


def test_rn01_stock_insuficiente_se_rechaza_sin_cambios(entorno):
    client, base = entorno
    empleado = sesion(client, "empleado")
    reparacion = tomar(client, empleado)
    ruta = f"/api/v0/reparaciones/{reparacion['id']}/usos"

    # Hay 8 en total, pero ninguna ubicación sola llega a 6.
    rechazo = client.post(ruta, headers=empleado, json={"repuesto_id": 1, "cantidad": 6})

    assert (rechazo.status_code, rechazo.json()["codigo"]) == (409, "stock_insuficiente")
    assert (existencia(base, 1, 1), existencia(base, 1, 2)) == ((5, 0), (3, 0))
    assert consultar(base, "SELECT count(*) FROM usos_repuestos_reparacion") == [(0,)]
    assert consultar(base, "SELECT count(*) FROM movimientos_stock") == [(0,)]
    # Exactamente lo disponible sí alcanza y deja el físico en cero.
    exacto = client.post(ruta, headers=empleado, json={"repuesto_id": 1, "cantidad": 5, "ubicacion_id": 1})
    assert exacto.status_code == 201, exacto.text
    assert existencia(base, 1, 1) == (0, 0)
    # Un repuesto sin existencias no tiene de dónde descontar.
    sin_stock = client.post(ruta, headers=empleado, json={"repuesto_id": 3, "cantidad": 1})
    assert (sin_stock.status_code, sin_stock.json()["codigo"]) == (409, "stock_insuficiente")


def test_rn01_no_usa_lo_reservado_para_otra_tarea(entorno):
    client, base = entorno
    empleado = sesion(client, "empleado")
    reparacion = tomar(client, empleado)
    ruta = f"/api/v0/reparaciones/{reparacion['id']}/usos"

    # REP-2 tiene 4 físicas pero 3 reservadas (RN-05): solo 1 disponible.
    rechazo = client.post(ruta, headers=empleado, json={"repuesto_id": 2, "cantidad": 2})
    assert (rechazo.status_code, rechazo.json()["codigo"]) == (409, "stock_insuficiente")
    assert existencia(base, 2, 1) == (4, 3)

    assert client.post(ruta, headers=empleado, json={"repuesto_id": 2, "cantidad": 1}).status_code == 201
    assert existencia(base, 2, 1) == (3, 3)


def test_rn02_el_uso_puede_disparar_la_alerta_de_umbral(entorno):
    client, _ = entorno
    empleado = sesion(client, "empleado")
    reparacion = tomar(client, empleado)

    def en_alerta() -> bool:
        alertas = client.get("/api/v0/stock/alertas", headers=empleado).json()["items"]
        return "REP-1" in {a["repuesto"]["codigo"] for a in alertas}

    # REP-1: 8 disponibles, mínimo 5.
    assert not en_alerta()
    client.post(
        f"/api/v0/reparaciones/{reparacion['id']}/usos", headers=empleado, json={"repuesto_id": 1, "cantidad": 3}
    )
    assert en_alerta()


def test_errores_del_flujo(entorno):
    client, _ = entorno
    empleado = sesion(client, "empleado")

    # Se puede tomar una incidencia en triage, pero no una resuelta ni dos veces la misma.
    assert tomar(client, empleado, 2)["estado"] == "en_curso"
    resuelta = client.post("/api/v0/incidencias/3/reparacion", headers=empleado)
    assert (resuelta.status_code, resuelta.json()["codigo"]) == (409, "estado_invalido")
    reparacion = tomar(client, empleado, 1)
    repetida = client.post("/api/v0/incidencias/1/reparacion", headers=empleado)
    assert (repetida.status_code, repetida.json()["codigo"]) == (409, "incidencia_ya_tomada")
    assert client.post("/api/v0/incidencias/999/reparacion", headers=empleado).json()["codigo"] == "incidencia_inexistente"

    ruta = f"/api/v0/reparaciones/{reparacion['id']}/usos"
    assert client.post(ruta, headers=empleado, json={"repuesto_id": 999, "cantidad": 1}).json()["codigo"] == "repuesto_inexistente"
    assert client.post(ruta, headers=empleado, json={"repuesto_id": 1, "cantidad": 0}).status_code == 422
    assert client.post(ruta, headers=empleado, json={"repuesto_id": 1, "cantidad": 1.5}).status_code == 422
    assert client.get("/api/v0/reparaciones/999", headers=empleado).json()["codigo"] == "reparacion_inexistente"
    assert client.post("/api/v0/reparaciones/999/usos", headers=empleado, json={"repuesto_id": 1, "cantidad": 1}).status_code == 404
    assert client.post(f"/api/v0/reparaciones/{reparacion['id']}/informe", headers=empleado, json={"resumen": ""}).status_code == 422


def test_permisos_por_rol(entorno):
    client, _ = entorno
    cabeceras = {nombre: sesion(client, nombre) for nombre in ROLES}
    reparacion = tomar(client, cabeceras["empleado"])

    for nombre in ("operario", "encargado", "gerencia"):
        assert client.post("/api/v0/incidencias/2/reparacion", headers=cabeceras[nombre]).status_code == 403
        uso = client.post(
            f"/api/v0/reparaciones/{reparacion['id']}/usos",
            headers=cabeceras[nombre],
            json={"repuesto_id": 1, "cantidad": 1},
        )
        assert uso.status_code == 403
        informe = client.post(
            f"/api/v0/reparaciones/{reparacion['id']}/informe", headers=cabeceras[nombre], json={"resumen": "x"}
        )
        assert informe.status_code == 403
    consulta = {
        nombre: client.get(f"/api/v0/reparaciones/{reparacion['id']}", headers=cabeceras[nombre]).status_code
        for nombre in ROLES
    }
    assert consulta == {"operario": 403, "empleado": 200, "encargado": 200, "gerencia": 200}
    assert client.get(f"/api/v0/reparaciones/{reparacion['id']}").status_code == 401
    assert client.post("/api/v0/incidencias/2/reparacion").status_code == 401
