"""Cobertura de la base de prueba que carga datos_prueba.py."""

import sqlite3
from pathlib import Path

from typer.testing import CliRunner

import datos_prueba as modulo_datos_prueba
from autenticacion_jwt import verificar_contrasena
from datos_prueba import aplicacion as datos_prueba
from gestionar_acceso import aplicacion as gestionar_acceso
from dummy_db.paso_02_catalogo import MAQUINAS, REPUESTOS
from dummy_db.paso_03_incidencias import INCIDENCIAS, REPARACIONES
from dummy_db.paso_04_compras import PEDIDOS_COMPRA
from dummy_db.paso_05_stock import RESERVAS


def _configurar(tmp_path: Path) -> tuple[Path, Path]:
    base = tmp_path / "prueba.sqlite3"
    config = tmp_path / "config.toml"
    original = Path("config.toml").read_text(encoding="utf-8")
    config.write_text(
        original.replace('DB_NAME = "data/db.sqlite3"', f'DB_NAME = "{base.as_posix()}"'),
        encoding="utf-8",
    )
    return config, base


def _cargar(config: Path, *extra: str, entrada: str | None = None):
    cargar_config = modulo_datos_prueba.load_config
    modulo_datos_prueba.load_config = lambda entorno, reload: cargar_config(config, reload=reload)
    try:
        return CliRunner().invoke(
            datos_prueba, ["--config", "dev", *extra], input=entrada
        )
    finally:
        modulo_datos_prueba.load_config = cargar_config


def test_config_solo_acepta_nombre_de_entorno():
    resultado = CliRunner().invoke(datos_prueba, ["--config", "config.dev.toml"])
    assert resultado.exit_code != 0
    assert "nombre de entorno" in resultado.output


def test_datos_dummy_tienen_referencias_y_cantidades_coherentes():
    maquinas = {fila[0] for fila in MAQUINAS}
    repuestos = {fila[0]: (fila[-2], fila[-1]) for fila in REPUESTOS}
    incidencias = {fila[0] for fila in INCIDENCIAS}
    assert len(maquinas) == len(MAQUINAS)
    assert len(repuestos) == len(REPUESTOS)
    assert len(incidencias) == len(INCIDENCIAS)
    assert all(fila[1] in maquinas for fila in INCIDENCIAS)
    assert all(fila[0] in incidencias for fila in REPARACIONES)
    for pedido in PEDIDOS_COMPRA:
        solicitados = dict(pedido[-2])
        recibidos = {}
        for _, items in pedido[-1]:
            for codigo, ubicacion, cantidad in items:
                assert codigo in solicitados
                assert repuestos[codigo][0] == ubicacion
                recibidos[codigo] = recibidos.get(codigo, 0) + cantidad
        assert all(cantidad <= solicitados[codigo] for codigo, cantidad in recibidos.items())
    reservados = {}
    for *_, items in RESERVAS:
        for codigo, ubicacion, cantidad in items:
            assert repuestos[codigo][0] == ubicacion
            reservados[codigo] = reservados.get(codigo, 0) + cantidad
    assert all(cantidad <= repuestos[codigo][1] for codigo, cantidad in reservados.items())


def test_carga_datos_coherentes(tmp_path):
    config, base = _configurar(tmp_path)

    resultado = _cargar(config)

    assert resultado.exit_code == 0, resultado.output
    assert "10 reparaciones" in resultado.output
    with sqlite3.connect(base) as db:
        assert db.execute("SELECT count(*) FROM maquinas").fetchone()[0] == 18
        assert db.execute("SELECT count(*) FROM repuestos").fetchone()[0] == 13
        assert db.execute("SELECT count(*) FROM incidencias").fetchone()[0] == 19
        assert db.execute("SELECT count(*) FROM fotos_incidencias").fetchone()[0] == 3
        assert db.execute("SELECT count(*) FROM reparaciones").fetchone()[0] == 10
        assert db.execute("SELECT count(*) FROM informes_resolucion").fetchone()[0] == 3
        estados_reparacion = dict(db.execute("SELECT estado, count(*) FROM reparaciones GROUP BY estado"))
        assert estados_reparacion == {"en_curso": 5, "pendiente_repuesto": 2, "completada": 3}
        assert db.execute("""
            SELECT count(*) FROM reparaciones r JOIN incidencias i ON i.id = r.incidencia_id
            WHERE (r.estado = 'en_curso' AND i.estado != 'en_reparacion')
               OR (r.estado = 'pendiente_repuesto' AND i.estado != 'pendiente_repuesto')
               OR (r.estado = 'completada' AND i.estado != 'resuelta')
               OR r.iniciada_en < i.reportada_en
               OR (r.completada_en IS NOT NULL AND r.completada_en < r.iniciada_en)
        """).fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM pedidos_compra").fetchone()[0] == 9
        assert db.execute("SELECT count(*) FROM recepciones_compra").fetchone()[0] == 3
        assert db.execute("SELECT count(*) FROM reservas").fetchone()[0] == 3
        assert db.execute("SELECT count(DISTINCT estado) FROM incidencias").fetchone()[0] == 5
        hashes = db.execute("SELECT hash_contrasena FROM usuarios").fetchall()
        assert len(hashes) == 5
        assert all(verificar_contrasena("test", valor) for (valor,) in hashes)
        # El stock de cada ubicación es la suma de sus movimientos (RN-06).
        descuadrados = db.execute(
            """
            SELECT x.repuesto_id FROM repuestos_x_ubicaciones x
            LEFT JOIN movimientos_stock m
              ON m.repuesto_id = x.repuesto_id AND m.ubicacion_id = x.ubicacion_id
            GROUP BY x.repuesto_id, x.ubicacion_id
            HAVING x.cantidad_fisica != coalesce(sum(m.variacion_fisica), 0)
                OR x.cantidad_reservada != coalesce(sum(m.variacion_reservada), 0)
            """
        ).fetchall()
        assert descuadrados == []
        reservado = db.execute("SELECT sum(cantidad_reservada) FROM repuestos_x_ubicaciones").fetchone()[0]
        en_reservas = db.execute("SELECT sum(cantidad - cantidad_consumida) FROM items_reserva").fetchone()[0]
        assert reservado == en_reservas
        # Hay repuestos en alerta (RN-02) y repuestos con stock suficiente.
        disponibles = db.execute(
            """
            SELECT sum(x.cantidad_fisica - x.cantidad_reservada) <= r.stock_minimo
            FROM repuestos r JOIN repuestos_x_ubicaciones x ON x.repuesto_id = r.id
            GROUP BY r.id
            """
        ).fetchall()
        assert {en_alerta for (en_alerta,) in disponibles} == {0, 1}
        estados_pedido = {estado for (estado,) in db.execute("SELECT estado FROM pedidos_compra")}
        assert estados_pedido == {
            "creado", "pendiente_revision", "pendiente_aprobacion", "confirmado",
            "cancelado", "pendiente_recepcion", "recibido",
        }
        roles = {rol for (rol,) in db.execute("SELECT nombre FROM roles")}
        assert roles == {
            "operario_maquina", "empleado_mantenimiento",
            "encargado_mantenimiento", "gerencia_administracion",
        }
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []


def test_no_duplica_y_reinicia_sin_tocar_usuarios(tmp_path):
    config, base = _configurar(tmp_path)
    assert _cargar(config).exit_code == 0
    with sqlite3.connect(base) as db:
        db.execute(
            "INSERT INTO incidencias (maquina_id, reportada_por_usuario_id, descripcion, estado, turno)"
            " VALUES (1, 1, 'agregada a mano', 'reportada', 'tarde')"
        )

    repetida = _cargar(config)
    assert repetida.exit_code == 0, repetida.output
    assert "no se cargó nada" in repetida.output
    with sqlite3.connect(base) as db:
        assert db.execute("SELECT count(*) FROM maquinas").fetchone()[0] == 18
        assert db.execute("SELECT count(*) FROM incidencias").fetchone()[0] == 20

    reiniciada = _cargar(config, "--recreate", "--si")
    assert reiniciada.exit_code == 0, reiniciada.output
    with sqlite3.connect(base) as db:
        assert db.execute("SELECT count(*) FROM maquinas").fetchone()[0] == 18
        assert db.execute("SELECT count(*) FROM incidencias WHERE descripcion = 'agregada a mano'").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM usuarios").fetchone()[0] == 5
        hash_operario = db.execute(
            "SELECT hash_contrasena FROM usuarios WHERE correo = 'operario@test'"
        ).fetchone()[0]
    assert verificar_contrasena("test", hash_operario)


def test_reutiliza_los_usuarios_de_preparar_demo(tmp_path):
    config, base = _configurar(tmp_path)
    contrasenas = "".join("Original1234\nOriginal1234\n" for _ in range(4))
    demo = CliRunner().invoke(
        gestionar_acceso, ["preparar-demo", "--config", str(config)], input=contrasenas
    )
    assert demo.exit_code == 0, demo.output

    # Solo falta el segundo operario, que recibe la contraseña dummy.
    resultado = _cargar(config)

    assert resultado.exit_code == 0, resultado.output
    with sqlite3.connect(base) as db:
        assert db.execute("SELECT count(*) FROM usuarios").fetchone()[0] == 5
        hash_encargado = db.execute(
            "SELECT hash_contrasena FROM usuarios WHERE correo = 'encargado@test'"
        ).fetchone()[0]
    assert verificar_contrasena("Original1234", hash_encargado)
