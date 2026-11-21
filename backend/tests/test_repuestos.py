
"""Pruebas HTTP de repuestos y ubicaciones con base y tokens locales."""

import sqlite3
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app import create_app
from autenticacion_jwt import crear_token_jwt
from autorizacion_roles import obtener_usuario_actual
from utils import load_config, update_config


def con_rol(app, rol: str) -> None:
    app.dependency_overrides[obtener_usuario_actual] = lambda: SimpleNamespace(
        roles=[SimpleNamespace(nombre=rol)]
    )


def test_repuestos_ubicaciones_y_stock(tmp_path):
    """Prueba repuestos y ubicaciones utilizando roles simulados."""
    configuracion = load_config(reload=True)

    jwt = configuracion.auth.JWT.model_copy(
        update={"HABILITADO": False}
    )
    auth = configuracion.auth.model_copy(update={"JWT": jwt})

    cfg = update_config({
        "database": {
            "DB_NAME": (tmp_path / "repuestos.sqlite3").as_posix()
        },
        "auth": auth,
    })

    app = create_app(cfg=cfg)
    con_rol(app, "empleado_mantenimiento")

    with TestClient(app) as client:
        estante = client.post(
            "/api/v0/ubicaciones",
            json={
                "codigo": "A-03-12",
                "descripcion": "Estante A",
            },
        )
        assert estante.status_code == 201
        assert estante.json()["activo"] is True

        duplicada = client.post(
            "/api/v0/ubicaciones",
            json={"codigo": "A-03-12"},
        )
        assert duplicada.json()["codigo"] == "duplicado"

        client.post(
            "/api/v0/ubicaciones",
            json={"codigo": "B-01-04"},
        )

        assert client.get("/api/v0/ubicaciones").json()["total"] == 2

        con_rol(app, "encargado_mantenimiento")
        creado = client.post(
            "/api/v0/repuestos",
            json={
                "codigo": "REP-142",
                "nombre": "Rodamiento 6205",
                "descripcion": "Sellado",
                "stock_minimo": 5,
            },
        )
        assert creado.status_code == 201, creado.text
        assert creado.json()["stock"] == []
        assert creado.json()["stock_disponible_total"] == 0

        client.post(
            "/api/v0/repuestos",
            json={
                "codigo": "REP-087",
                "nombre": "Filtro de aceite",
                "stock_minimo": 0,
            },
        )

        duplicado = client.post(
            "/api/v0/repuestos",
            json={
                "codigo": "REP-142",
                "nombre": "Otro",
                "stock_minimo": 0,
            },
        )
        assert duplicado.status_code == 409
        assert duplicado.json()["codigo"] == "duplicado"

        con_rol(app, "empleado_mantenimiento")

        # Las existencias se insertan directamente porque las recepciones
        # están fuera del alcance de estas pruebas.
        ruta = tmp_path / "repuestos.sqlite3"

        with sqlite3.connect(ruta) as db:
            db.execute(
                """
                INSERT INTO repuestos_x_ubicaciones
                    (repuesto_id, ubicacion_id,
                     cantidad_fisica, cantidad_reservada)
                VALUES
                    (1, 1, 7, 2),
                    (1, 2, 3, 0)
                """
            )

        detalle = client.get("/api/v0/repuestos/1").json()

        assert [
            stock["ubicacion"]["codigo"]
            for stock in detalle["stock"]
        ] == ["A-03-12", "B-01-04"]

        assert detalle["stock"][0]["cantidad_disponible"] == 5

        assert (
            detalle["stock_fisico_total"],
            detalle["stock_reservado_total"],
        ) == (10, 2)

        assert detalle["stock_disponible_total"] == 8

        pagina = client.get("/api/v0/repuestos?limit=1").json()

        assert (
            pagina["total"],
            len(pagina["items"]),
            pagina["limit"],
        ) == (2, 1, 1)

        assert (
            client.get("/api/v0/repuestos?buscar=filtro")
            .json()["items"][0]["codigo"]
            == "REP-087"
        )

        assert (
            client.get("/api/v0/repuestos?buscar=sellado")
            .json()["total"]
            == 1
        )

        assert (
            client.get("/api/v0/repuestos?buscar=rep-")
            .json()["total"]
            == 2
        )

        assert (
            client.get("/api/v0/repuestos/codigo/REP-142")
            .json()["id"]
            == 1
        )

        assert (
            client.get("/api/v0/repuestos/codigo/NO-EXISTE")
            .json()["codigo"]
            == "repuesto_inexistente"
        )

        assert client.get("/api/v0/repuestos/999").status_code == 404

        editado = client.patch(
            "/api/v0/repuestos/1",
            json={"stock_minimo": 9, "activo": False},
        )
        assert editado.status_code == 200

        assert (
            editado.json()["stock_minimo"],
            editado.json()["activo"],
        ) == (9, False)

        assert editado.json()["actualizado_en"] is not None
        assert editado.json()["nombre"] == "Rodamiento 6205"

        assert client.patch(
            "/api/v0/repuestos/1",
            json={"nombre": None},
        ).status_code == 422

        assert client.patch(
            "/api/v0/repuestos/2",
            json={"codigo": "REP-142"},
        ).status_code == 409

        assert client.patch(
            "/api/v0/repuestos/999",
            json={"nombre": "x"},
        ).status_code == 404

        con_rol(app, "gerencia_administracion")

        assert client.get("/api/v0/repuestos").status_code == 200

        assert client.post(
            "/api/v0/ubicaciones",
            json={"codigo": "Z-1"},
        ).status_code == 403

        assert client.patch(
            "/api/v0/repuestos/1",
            json={"nombre": "x"},
        ).status_code == 403

        con_rol(app, "encargado_mantenimiento")

        assert client.post(
            "/api/v0/ubicaciones",
            json={"codigo": "C-02-11"},
        ).status_code == 201

        con_rol(app, "operario_maquina")

        assert client.get("/api/v0/repuestos").status_code == 403
        assert client.get("/api/v0/ubicaciones").status_code == 403


def test_repuestos_exigen_token_y_rol_vigente(tmp_path):
    """Comprueba autenticación JWT y autorización con roles persistidos."""
    ruta = tmp_path / "seguridad.sqlite3"

    configuracion = load_config(reload=True)

    jwt = configuracion.auth.JWT.model_copy(
        update={"HABILITADO": True}
    )
    auth = configuracion.auth.model_copy(update={"JWT": jwt})

    configuracion = update_config({
        "database": {"DB_NAME": ruta.as_posix()},
        "auth": auth,
        "secrets": {"CLAVE_JWT": "x" * 64},
    })

    app = create_app(cfg=configuracion)

    with TestClient(app) as client:
        assert client.get("/api/v0/repuestos").status_code == 401

        assert (
            client.get("/api/v0/ubicaciones").json()["codigo"]
            == "no_autorizado"
        )

        with sqlite3.connect(ruta) as db:
            db.execute(
                """
                INSERT INTO usuarios
                    (id, nombre, apellido, genero, correo,
                     hash_contrasena, verificado)
                VALUES
                    (1, 'Ernesto', 'Demo', 'M',
                     'empleado@example.invalid', 'hash', 0)
                """
            )

            db.execute(
                "INSERT INTO roles (id, nombre) "
                "VALUES (1, 'empleado_mantenimiento')"
            )

            db.execute(
                "INSERT INTO usuarios_x_roles (usuario_id, rol_id) "
                "VALUES (1, 1)"
            )

        token, _ = crear_token_jwt(
            configuracion,
            1,
            roles=["empleado_mantenimiento"],
        )

        cabecera = {"Authorization": f"Bearer {token}"}

        respuesta = client.post(
            "/api/v0/ubicaciones",
            headers=cabecera,
            json={"codigo": "A-01"},
        )
        assert respuesta.status_code == 201

        assert (
            client.get(
                "/api/v0/ubicaciones",
                headers=cabecera,
            ).json()["total"]
            == 1
        )

        # Los roles se leen de la base en cada solicitud,
        # no del token.
        with sqlite3.connect(ruta) as db:
            db.execute("DELETE FROM usuarios_x_roles")

        assert client.get(
            "/api/v0/ubicaciones",
            headers=cabecera,
        ).status_code == 403
