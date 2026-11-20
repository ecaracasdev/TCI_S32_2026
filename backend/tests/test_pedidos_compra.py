
"""Pruebas HTTP de pedidos de compra y recepción de stock."""

import sqlite3

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


def cargar_datos(base):
    """Carga usuarios, roles, ubicaciones y repuestos para las pruebas."""
    conexion = sqlite3.connect(base)

    try:
        cursor = conexion.cursor()

        usuarios = [
            (1, "Operario", "Prueba", "M", "operario@test.com", ROLES["operario"]),
            (2, "Empleado", "Prueba", "M", "empleado@test.com", ROLES["empleado"]),
            (3, "Encargado", "Prueba", "M", "encargado@test.com", ROLES["encargado"]),
            (4, "Gerencia", "Prueba", "M", "gerencia@test.com", ROLES["gerencia"]),
        ]

        for rol_id, nombre_rol in enumerate(ROLES.values(), start=1):
            cursor.execute(
                "INSERT INTO roles (id, nombre) VALUES (?, ?)",
                (rol_id, nombre_rol),
            )

        for usuario_id, nombre, apellido, genero, correo, rol in usuarios:
            cursor.execute(
                """
                INSERT INTO usuarios (
                    id, nombre, apellido, genero, correo,
                    hash_contrasena, verificado
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    usuario_id,
                    nombre,
                    apellido,
                    genero,
                    correo,
                    crear_hash_contrasena(CONTRASENA),
                    1,
                ),
            )

            rol_id = list(ROLES.values()).index(rol) + 1
            cursor.execute(
                """
                INSERT INTO usuarios_x_roles (usuario_id, rol_id)
                VALUES (?, ?)
                """,
                (usuario_id, rol_id),
            )

        cursor.execute(
            """
            INSERT INTO ubicaciones (id, codigo, activo)
            VALUES (1, 'DEP-01', 1)
            """
        )

        cursor.execute(
            """
            INSERT INTO repuestos (id, codigo, nombre, stock_minimo)
            VALUES (1, 'REP-01', 'Repuesto de prueba', 2)
            """
        )

        cursor.execute(
            """
            INSERT INTO repuestos_x_ubicaciones (
                repuesto_id, ubicacion_id,
                cantidad_fisica, cantidad_reservada
            )
            VALUES (1, 1, 10, 0)
            """
        )

        conexion.commit()
    finally:
        conexion.close()


@pytest.fixture
def entorno(tmp_path):
    """Crea una aplicación y una base SQLite aisladas."""
    base = tmp_path / "pedidos_compra.db"

    configuracion = load_config(reload=True)
    jwt = configuracion.auth.JWT.model_copy(update={"HABILITADO": True})

    aplicacion = create_app(
        cfg=update_config(
            {
                "database": {"DB_NAME": base.as_posix()},
                "auth": configuracion.auth.model_copy(update={"JWT": jwt}),
                "secrets": {"CLAVE_JWT": "x" * 64},
            }
        )
    )

    with TestClient(aplicacion) as cliente:
        cargar_datos(base)
        yield cliente, base

    load_config(reload=True)


def sesion(cliente, correo):
    """Obtiene un token para el usuario indicado."""
    respuesta = cliente.post(
        "/auth/token",
        data={
            "username": correo,
            "password": CONTRASENA,
            "grant_type": "password",
        },
    )

    assert respuesta.status_code == 200, respuesta.text

    token = respuesta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def existencia(base):
    """Devuelve el stock físico y reservado del repuesto de prueba."""
    conexion = sqlite3.connect(base)

    try:
        return conexion.execute(
            """
            SELECT cantidad_fisica, cantidad_reservada
            FROM repuestos_x_ubicaciones
            WHERE repuesto_id = 1 AND ubicacion_id = 1
            """
        ).fetchone()
    finally:
        conexion.close()


def cantidad_movimientos(base):
    """Cuenta los movimientos de recepción de compra."""
    conexion = sqlite3.connect(base)

    try:
        return conexion.execute(
            """
            SELECT COUNT(*)
            FROM movimientos_stock
            WHERE tipo_movimiento = 'recepcion_compra'
            """
        ).fetchone()[0]
    finally:
        conexion.close()


def crear_pedido(cliente, headers, cantidad=5):
    """Crea un pedido con una partida."""
    return cliente.post(
        "/api/v0/pedidos-compra",
        headers=headers,
        json={
            "urgencia": "normal",
            "motivo": "Reposición de stock",
            "items": [
                {
                    "repuesto_id": 1,
                    "cantidad_solicitada": cantidad,
                }
            ],
        },
    )


def avanzar_hasta_aprobacion(cliente, headers, pedido_id):
    """Avanza el pedido hasta el estado pendiente de aprobación."""
    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido_id}/asignacion",
        headers=headers,
        json={"asignado_a_usuario_id": 2},
    )
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["estado"] == "pendiente_revision"

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido_id}/revision",
        headers=headers,
        json={"observaciones": "Revisión realizada"},
    )
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["estado"] == "pendiente_aprobacion"


def avanzar_hasta_confirmacion(cliente, headers, pedido_id):
    """Aprueba el pedido y lo deja listo para recibir."""
    avanzar_hasta_aprobacion(cliente, headers, pedido_id)

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido_id}/aprobacion",
        headers=headers,
        json={"observaciones": "Pedido aprobado"},
    )
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["estado"] == "confirmado"


def test_pedidos_compra_requiere_autenticacion(entorno):
    cliente, _ = entorno

    respuesta = cliente.get("/api/v0/pedidos-compra")

    assert respuesta.status_code == 401


def test_empleado_puede_crear_pedido(entorno):
    cliente, _ = entorno
    headers = sesion(cliente, "empleado@test.com")

    respuesta = crear_pedido(cliente, headers)

    assert respuesta.status_code == 201, respuesta.text
    datos = respuesta.json()

    assert datos["id"] > 0
    assert datos["estado"] == "creado"
    assert datos["origen"] == "manual"
    assert len(datos["items"]) == 1
    assert datos["items"][0]["cantidad_solicitada"] == 5


def test_operario_no_puede_crear_pedido(entorno):
    cliente, _ = entorno
    headers = sesion(cliente, "operario@test.com")

    respuesta = crear_pedido(cliente, headers)

    assert respuesta.status_code == 403


def test_empleado_no_puede_listar_pedidos(entorno):
    cliente, _ = entorno
    headers = sesion(cliente, "empleado@test.com")

    respuesta = cliente.get(
        "/api/v0/pedidos-compra",
        headers=headers,
    )

    assert respuesta.status_code == 403


def test_encargado_y_gerencia_pueden_listar(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    crear_pedido(cliente, empleado)

    for correo in ("encargado@test.com", "gerencia@test.com"):
        headers = sesion(cliente, correo)
        respuesta = cliente.get(
            "/api/v0/pedidos-compra",
            headers=headers,
        )

        assert respuesta.status_code == 200, respuesta.text
        datos = respuesta.json()

        assert len(datos["items"]) == 1
        assert datos["total"] == 1
        assert datos["offset"] == 0
        assert datos["limit"] == 50


def test_obtener_pedido_inexistente_devuelve_404(entorno):
    cliente, _ = entorno
    headers = sesion(cliente, "encargado@test.com")

    respuesta = cliente.get(
        "/api/v0/pedidos-compra/999",
        headers=headers,
    )

    assert respuesta.status_code == 404


def test_listado_puede_filtrar_por_estado(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    crear_pedido(cliente, empleado)

    respuesta = cliente.get(
        "/api/v0/pedidos-compra",
        headers=encargado,
        params={"estado": "creado"},
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["total"] == 1

    respuesta = cliente.get(
        "/api/v0/pedidos-compra",
        headers=encargado,
        params={"estado": "recibido"},
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["total"] == 0


def test_no_se_puede_asignar_un_pedido_en_estado_incorrecto(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado).json()

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido['id']}/revision",
        headers=encargado,
        json={},
    )

    assert respuesta.status_code == 409


def test_encargado_puede_asignar_pedido(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado).json()

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido['id']}/asignacion",
        headers=encargado,
        json={"asignado_a_usuario_id": 2},
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["estado"] == "pendiente_revision"
    assert respuesta.json()["asignado_a_usuario_id"] == 2


def test_encargado_puede_revisar_pedido(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado).json()

    asignacion = cliente.post(
        f"/api/v0/pedidos-compra/{pedido['id']}/asignacion",
        headers=encargado,
        json={"asignado_a_usuario_id": 2},
    )
    assert asignacion.status_code == 200, asignacion.text

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido['id']}/revision",
        headers=encargado,
        json={"observaciones": "Revisión aprobada"},
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["estado"] == "pendiente_aprobacion"


def test_encargado_puede_aprobar_pedido(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado).json()
    avanzar_hasta_aprobacion(cliente, encargado, pedido["id"])

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido['id']}/aprobacion",
        headers=encargado,
        json={"observaciones": "Aprobado"},
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["estado"] == "confirmado"


def test_encargado_puede_recibir_y_actualizar_stock(entorno):
    cliente, base = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado, cantidad=5).json()
    pedido_id = pedido["id"]

    avanzar_hasta_confirmacion(cliente, encargado, pedido_id)

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido_id}/confirmacion",
        headers=encargado,
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["estado"] == "pendiente_recepcion"

    item_id = pedido["items"][0]["id"]

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido_id}/recepciones",
        headers=encargado,
        json={
            "notas": "Recepción parcial",
            "items": [
                {
                    "item_pedido_compra_id": item_id,
                    "ubicacion_id": 1,
                    "cantidad": 2,
                }
            ],
        },
    )

    assert respuesta.status_code == 201, respuesta.text
    assert respuesta.json()["pedido_compra_id"] == pedido_id
    assert existencia(base) == (12, 0)
    assert cantidad_movimientos(base) == 1

    detalle = cliente.get(
        f"/api/v0/pedidos-compra/{pedido_id}",
        headers=encargado,
    )

    assert detalle.status_code == 200, detalle.text
    assert detalle.json()["estado"] == "pendiente_recepcion"

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido_id}/recepciones",
        headers=encargado,
        json={
            "notas": "Recepción final",
            "items": [
                {
                    "item_pedido_compra_id": item_id,
                    "ubicacion_id": 1,
                    "cantidad": 3,
                }
            ],
        },
    )

    assert respuesta.status_code == 201, respuesta.text
    assert existencia(base) == (15, 0)
    assert cantidad_movimientos(base) == 2

    detalle = cliente.get(
        f"/api/v0/pedidos-compra/{pedido_id}",
        headers=encargado,
    )

    assert detalle.status_code == 200, detalle.text
    assert detalle.json()["estado"] == "recibido"


def test_no_se_puede_recibir_mas_de_lo_solicitado(entorno):
    cliente, base = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado, cantidad=5).json()
    pedido_id = pedido["id"]

    avanzar_hasta_confirmacion(cliente, encargado, pedido_id)

    item_id = pedido["items"][0]["id"]

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido_id}/recepciones",
        headers=encargado,
        json={
            "items": [
                {
                    "item_pedido_compra_id": item_id,
                    "ubicacion_id": 1,
                    "cantidad": 6,
                }
            ],
        },
    )

    assert respuesta.status_code == 409
    assert existencia(base) == (10, 0)
    assert cantidad_movimientos(base) == 0


def test_empleado_no_puede_registrar_recepcion(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")

    respuesta = cliente.post(
        "/api/v0/pedidos-compra/1/recepciones",
        headers=empleado,
        json={"items": []},
    )

    assert respuesta.status_code == 403


def test_no_se_puede_cancelar_pedido_en_estado_creado(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado).json()

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido['id']}/cancelacion",
        headers=encargado,
        json={"motivo": "Ya no se necesita"},
    )

    assert respuesta.status_code == 409


def test_crear_pedido_con_datos_invalidos_devuelve_422(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")

    respuesta = cliente.post(
        "/api/v0/pedidos-compra",
        headers=empleado,
        json={"urgencia": "normal", "items": []},
    )

    assert respuesta.status_code == 422


def test_filtrar_por_estado_inexistente_devuelve_422(entorno):
    cliente, _ = entorno
    encargado = sesion(cliente, "encargado@test.com")

    respuesta = cliente.get(
        "/api/v0/pedidos-compra",
        headers=encargado,
        params={"estado": "inexistente"},
    )

    assert respuesta.status_code == 422


def test_listado_respeta_offset_y_limit(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    crear_pedido(cliente, empleado)
    crear_pedido(cliente, empleado)
    crear_pedido(cliente, empleado)

    respuesta = cliente.get(
        "/api/v0/pedidos-compra",
        headers=encargado,
        params={"offset": 1, "limit": 1},
    )

    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()

    assert len(datos["items"]) == 1
    assert datos["total"] == 3
    assert datos["offset"] == 1
    assert datos["limit"] == 1


def test_asignar_pedido_inexistente_devuelve_404(entorno):
    cliente, _ = entorno
    encargado = sesion(cliente, "encargado@test.com")

    respuesta = cliente.post(
        "/api/v0/pedidos-compra/999/asignacion",
        headers=encargado,
        json={"asignado_a_usuario_id": 2},
    )

    assert respuesta.status_code == 404


def test_revisar_pedido_inexistente_devuelve_404(entorno):
    cliente, _ = entorno
    encargado = sesion(cliente, "encargado@test.com")

    respuesta = cliente.post(
        "/api/v0/pedidos-compra/999/revision",
        headers=encargado,
        json={},
    )

    assert respuesta.status_code == 404


def test_aprobar_pedido_inexistente_devuelve_404(entorno):
    cliente, _ = entorno
    encargado = sesion(cliente, "encargado@test.com")

    respuesta = cliente.post(
        "/api/v0/pedidos-compra/999/aprobacion",
        headers=encargado,
        json={},
    )

    assert respuesta.status_code == 404


def test_encargado_puede_cancelar_pedido_pendiente(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado).json()
    avanzar_hasta_aprobacion(cliente, encargado, pedido["id"])

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido['id']}/cancelacion",
        headers=encargado,
        json={"motivo": "Ya no se necesita"},
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["estado"] == "cancelado"


def test_confirmar_pedido_en_estado_incorrecto_devuelve_409(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado).json()

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido['id']}/confirmacion",
        headers=encargado,
    )

    assert respuesta.status_code == 409


def test_recibir_pedido_inexistente_devuelve_404(entorno):
    cliente, _ = entorno
    encargado = sesion(cliente, "encargado@test.com")

    respuesta = cliente.post(
        "/api/v0/pedidos-compra/999/recepciones",
        headers=encargado,
        json={
            "items": [
                {
                    "item_pedido_compra_id": 1,
                    "ubicacion_id": 1,
                    "cantidad": 1,
                }
            ]
        },
    )

    assert respuesta.status_code == 404


def test_recibir_pedido_en_estado_incorrecto_devuelve_409(entorno):
    cliente, base = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado).json()
    item_id = pedido["items"][0]["id"]

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido['id']}/recepciones",
        headers=encargado,
        json={
            "items": [
                {
                    "item_pedido_compra_id": item_id,
                    "ubicacion_id": 1,
                    "cantidad": 1,
                }
            ]
        },
    )

    assert respuesta.status_code == 409
    assert existencia(base) == (10, 0)
    assert cantidad_movimientos(base) == 0



# ============================================================
# Tests específicos del caso de uso CUN-03
# ============================================================

# Reutilizamos las pruebas existentes de transiciones válidas,
# pero también las identificamos con el prefijo requerido.
test_cun03_asignacion_valida = test_encargado_puede_asignar_pedido
test_cun03_revision_valida = test_encargado_puede_revisar_pedido
test_cun03_aprobacion_valida = test_encargado_puede_aprobar_pedido
test_cun03_cancelacion_valida = test_encargado_puede_cancelar_pedido_pendiente


@pytest.mark.parametrize(
    "accion",
    ["asignacion", "revision", "aprobacion", "cancelacion"],
)
def test_cun03_transicion_invalida_devuelve_409_sin_modificar(
    entorno, accion
):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado).json()
    pedido_id = pedido["id"]

    if accion == "asignacion":
        primera = cliente.post(
            f"/api/v0/pedidos-compra/{pedido_id}/asignacion",
            headers=encargado,
            json={"asignado_a_usuario_id": 2},
        )
        assert primera.status_code == 200

        payload = {"asignado_a_usuario_id": 2}

    elif accion == "revision":
        payload = {"observaciones": "Revisión"}

    elif accion == "aprobacion":
        payload = {"observaciones": "Aprobación"}

    else:
        payload = {"motivo": "Cancelación"}

    antes = cliente.get(
        f"/api/v0/pedidos-compra/{pedido_id}",
        headers=encargado,
    )
    assert antes.status_code == 200
    estado_anterior = antes.json()["estado"]

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido_id}/{accion}",
        headers=encargado,
        json=payload,
    )

    assert respuesta.status_code == 409

    despues = cliente.get(
        f"/api/v0/pedidos-compra/{pedido_id}",
        headers=encargado,
    )
    assert despues.status_code == 200
    assert despues.json()["estado"] == estado_anterior


def test_cun03_cancelacion_sin_motivo_devuelve_422(entorno):
    cliente, _ = entorno
    empleado = sesion(cliente, "empleado@test.com")
    encargado = sesion(cliente, "encargado@test.com")

    pedido = crear_pedido(cliente, empleado).json()
    avanzar_hasta_aprobacion(cliente, encargado, pedido["id"])

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/{pedido['id']}/cancelacion",
        headers=encargado,
        json={},
    )

    assert respuesta.status_code == 422

    detalle = cliente.get(
        f"/api/v0/pedidos-compra/{pedido['id']}",
        headers=encargado,
    )
    assert detalle.json()["estado"] == "pendiente_aprobacion"


def test_cun03_cancelacion_pedido_inexistente_devuelve_404(entorno):
    cliente, _ = entorno
    encargado = sesion(cliente, "encargado@test.com")

    respuesta = cliente.post(
        "/api/v0/pedidos-compra/999/cancelacion",
        headers=encargado,
        json={"motivo": "Prueba"},
    )

    assert respuesta.status_code == 404


@pytest.mark.parametrize(
    "accion,payload",
    [
        ("asignacion", {"asignado_a_usuario_id": 2}),
        ("revision", {"observaciones": "Prueba"}),
        ("aprobacion", {"observaciones": "Prueba"}),
        ("cancelacion", {"motivo": "Prueba"}),
    ],
)
def test_cun03_operaciones_sin_autenticacion_devuelven_401(
    entorno, accion, payload
):
    cliente, _ = entorno

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/999/{accion}",
        json=payload,
    )

    assert respuesta.status_code == 401


@pytest.mark.parametrize(
    "correo",
    ["empleado@test.com", "gerencia@test.com"],
)
@pytest.mark.parametrize(
    "accion,payload",
    [
        ("asignacion", {"asignado_a_usuario_id": 2}),
        ("revision", {"observaciones": "Prueba"}),
        ("aprobacion", {"observaciones": "Prueba"}),
        ("cancelacion", {"motivo": "Prueba"}),
    ],
)
def test_cun03_rol_no_autorizado_devuelve_403(
    entorno, correo, accion, payload
):
    cliente, _ = entorno
    headers = sesion(cliente, correo)

    respuesta = cliente.post(
        f"/api/v0/pedidos-compra/999/{accion}",
        headers=headers,
        json=payload,
    )

    assert respuesta.status_code == 403
