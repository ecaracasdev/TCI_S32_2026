"""Paso 3: incidencias, reparaciones y consumos de repuestos."""
from datetime import datetime, timedelta, timezone
from db.db_models import IncidenciaDb, FotoIncidenciaDb, ReparacionDb, UsoRepuestoReparacionDb, MovimientoStockDb, InformeResolucionDb

ZONA_PLANTA = timezone(timedelta(hours=-3))

# (clave, máquina, reportada por, descripción, estado, hace cuánto se reportó, resuelta hace, con foto)
INCIDENCIAS = (
    ("i1", "F-02", "operario", "Vibración anormal en el motor del fraccionador.",
     "en_triage", timedelta(hours=3), None, False),
    ("i2", "B-04", "operario2", "La banda se desalinea y el producto se corre hacia un costado.",
     "en_reparacion", timedelta(days=1, hours=6), None, False),
    ("i3", "C-01", "operario", "Fuga en la válvula de presión de la caldera.",
     "en_triage", timedelta(hours=10), None, False),
    ("i4", "F-03", "operario2", "Temperatura elevada en el cabezal dosificador.",
     "reportada", timedelta(minutes=40), None, True),
    ("i5", "B-04", "operario", "Se cortó la correa dentada y la banda no arranca.",
     "pendiente_repuesto", timedelta(days=4), None, False),
    ("i6", "C-02", "operario", "La caldera tarda mucho en levantar presión al inicio del turno.",
     "resuelta", timedelta(days=7), timedelta(days=6), False),
    ("i7", "M-05", "operario2", "Ruido metálico en la paleta de mezcla al subir de velocidad.",
     "resuelta", timedelta(days=12), timedelta(days=11), False),
    ("i8", "C-03", "operario", "Variación de presión durante el encendido.", "reportada", timedelta(hours=1), None, False),
    ("i9", "F-04", "operario2", "Dosificación irregular en la línea.", "en_reparacion", timedelta(hours=5), None, False),
    ("i10", "B-05", "operario", "Ruido intermitente en el rodillo.", "reportada", timedelta(hours=8), None, False),
    ("i11", "P-04", "operario2", "Presión de trabajo inferior a la habitual.", "en_reparacion", timedelta(hours=12), None, False),
    ("i12", "M-06", "operario", "Vibración durante la mezcla.", "reportada", timedelta(days=1), None, False),
    ("i13", "E-07", "operario2", "El elevador se detiene brevemente entre pisos.", "en_reparacion", timedelta(days=2), None, False),
    ("i14", "F-01", "operario", "Pérdida de producto en la tolva.", "reportada", timedelta(hours=4), None, False),
    ("i15", "C-02", "operario2", "Lectura irregular del sensor de temperatura.", "en_triage", timedelta(days=1, hours=2), None, False),
    ("i16", "P-05", "operario", "Pérdida de presión en el cilindro.", "en_reparacion", timedelta(days=2), None, True),
    ("i17", "C-04", "operario2", "El manómetro no regresa a cero.", "resuelta", timedelta(days=10), timedelta(days=8), True),
    ("i18", "M-07", "operario", "Desgaste del acople del agitador.", "pendiente_repuesto", timedelta(days=3), None, False),
    ("i19", "P-04", "operario2", "Pérdida intermitente en el circuito hidráulico.", "reportada", timedelta(minutes=30), None, False),
)

# (incidencia, estado, iniciada hace, completada hace, usos [(repuesto, cantidad)], informe)
REPARACIONES = (
    ("i2", "en_curso", timedelta(days=1), None, (("REP-00142", 1),), None),
    ("i5", "pendiente_repuesto", timedelta(days=3, hours=20), None, (), None),
    ("i6", "completada", timedelta(days=6, hours=20), timedelta(days=6), (("REP-00087", 2),),
     "Se reemplazaron los dos filtros de aceite obstruidos y se purgó el circuito."),
    ("i7", "completada", timedelta(days=11, hours=22), timedelta(days=11), (("REP-00090", 1),),
     "Se cambió la paleta de mezcla con desgaste en el borde de ataque."),
    ("i16", "en_curso", timedelta(days=1, hours=20), None, (("REP-00302", 1),), None),
    ("i17", "completada", timedelta(days=9), timedelta(days=8), (("REP-00301", 1),),
     "Se reemplazó y calibró el manómetro de la caldera."),
    ("i18", "pendiente_repuesto", timedelta(days=2), None, (), None),
    ("i9", "en_curso", timedelta(hours=3), None, (), None),
    ("i11", "en_curso", timedelta(hours=8), None, (), None),
    ("i13", "en_curso", timedelta(days=1), None, (), None),
)

# PNG de 1x1 px: alcanza para probar el alta y la lectura de evidencias.
FOTO_PRUEBA = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


def turno_de(fecha: datetime) -> str:
    hora = fecha.astimezone(ZONA_PLANTA).hour
    if 6 <= hora < 14:
        return "manana"
    if 14 <= hora < 22:
        return "tarde"
    return "noche"




async def cargar(sesion, contexto):
    ahora, usuarios = contexto["ahora"], contexto["usuarios"]
    maquinas, repuestos, ubicaciones = (contexto[k] for k in ("maquinas", "repuestos", "ubicaciones"))
    ubicacion_de, fisico, movimientos = (contexto[k] for k in ("ubicacion_de", "fisico", "movimientos"))
    incidencias = {}
    for clave, maquina, reporto, descripcion, estado, hace, resuelta_hace, con_foto in INCIDENCIAS:
        reportada_en = ahora - hace
        incidencia = IncidenciaDb(
            maquina_id=maquinas[maquina].id,
            reportada_por_usuario_id=usuarios[reporto],
            descripcion=descripcion,
            estado=estado,
            turno=turno_de(reportada_en),
            reportada_en=reportada_en,
            resuelta_en=ahora - resuelta_hace if resuelta_hace else None,
        )
        sesion.add(incidencia)
        incidencias[clave] = incidencia
    await sesion.flush()
    for clave, *_, con_foto in INCIDENCIAS:
        if con_foto:
            sesion.add(
                FotoIncidenciaDb(
                    incidencia_id=incidencias[clave].id,
                    contenido_base64=FOTO_PRUEBA,
                    nombre_archivo="cabezal.png",
                    tipo_mime="image/png",
                    capturada_en=incidencias[clave].reportada_en,
                )
            )

    for clave, estado, iniciada_hace, completada_hace, usos, informe in REPARACIONES:
        reparacion = ReparacionDb(
            incidencia_id=incidencias[clave].id,
            empleado_id=usuarios["empleado"],
            estado=estado,
            iniciada_en=ahora - iniciada_hace,
            completada_en=ahora - completada_hace if completada_hace else None,
        )
        sesion.add(reparacion)
        await sesion.flush()
        for repuesto, cantidad in usos:
            uso = UsoRepuestoReparacionDb(
                reparacion_id=reparacion.id,
                repuesto_id=repuestos[repuesto].id,
                cantidad=cantidad,
                usada_por_usuario_id=usuarios["empleado"],
                usada_en=reparacion.iniciada_en + timedelta(hours=2),
            )
            sesion.add(uso)
            await sesion.flush()
            ubicacion = ubicacion_de[repuesto]
            fisico[repuesto, ubicacion] -= cantidad
            movimientos.append(
                MovimientoStockDb(
                    repuesto_id=repuestos[repuesto].id,
                    ubicacion_id=ubicaciones[ubicacion].id,
                    tipo_movimiento="consumo",
                    cantidad=cantidad,
                    variacion_fisica=-cantidad,
                    variacion_reservada=0,
                    realizado_por_usuario_id=usuarios["empleado"],
                    ocurrido_en=uso.usada_en,
                    motivo=f"Uso en la reparación de la incidencia {incidencias[clave].id}.",
                    uso_repuesto_reparacion_id=uso.id,
                )
            )
        if informe:
            sesion.add(
                InformeResolucionDb(
                    reparacion_id=reparacion.id,
                    empleado_id=usuarios["empleado"],
                    resumen=informe,
                    creada_en=reparacion.completada_en,
                )
            )

    contexto["incidencias"] = incidencias
