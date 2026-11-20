"""Paso 4: pedidos de compra y sus recepciones."""
from datetime import timedelta
from db.db_models import PedidoCompraDb, ItemPedidoCompraDb, RecepcionCompraDb, ItemRecepcionCompraDb, MovimientoStockDb

# (estado, urgencia, origen, creado por, asignado a, revisión resuelta por, motivo,
#  motivo de cancelación, hace cuánto, items [(repuesto, cantidad)],
#  recepciones [(recibida hace, [(repuesto, ubicación, cantidad)])])
PEDIDOS_COMPRA = (
    ("creado", "normal", "manual", "empleado", None, None,
     "Reposición preventiva de filtros.", None, timedelta(hours=2),
     (("REP-00087", 8),), ()),
    ("pendiente_revision", "urgente", "automatico", "empleado", None, None,
     "Stock por debajo del mínimo.", None, timedelta(hours=6),
     (("REP-00142", 12),), ()),
    ("pendiente_aprobacion", "normal", "manual", "empleado", "encargado", None,
     None, None, timedelta(days=1),
     (("REP-00058", 4),), ()),
    ("confirmado", "urgente", "manual", "empleado", "encargado", "encargado",
     "Correa cortada en la banda B-04, línea detenida.", None, timedelta(days=3, hours=22),
     (("REP-00203", 4),), ()),
    ("cancelado", "normal", "manual", "empleado", None, "encargado",
     None, "Pedido duplicado.", timedelta(days=5),
     (("REP-00031", 3),), ()),
    ("pendiente_recepcion", "urgente", "manual", "encargado", "encargado", "encargado",
     None, None, timedelta(days=9),
     (("REP-00215", 2), ("REP-00174", 2)),
     ((timedelta(days=8), (("REP-00174", "B-02-05", 1),)),)),
    ("recibido", "normal", "automatico", "empleado", "encargado", "encargado",
     "Reposición por nivel mínimo.", None, timedelta(days=15),
     (("REP-00106", 5),),
     ((timedelta(days=14), (("REP-00106", "B-04-02", 5),)),)),
    ("pendiente_recepcion", "normal", "manual", "empleado", "encargado", "encargado",
     "Reposición de sellos hidráulicos.", None, timedelta(days=12),
     (("REP-00302", 4),),
     ((timedelta(days=11), (("REP-00302", "B-01-04", 2),)),)),
    ("pendiente_aprobacion", "urgente", "manual", "empleado", "encargado", None,
     "Acople requerido para la mezcladora M-07.", None, timedelta(hours=12),
     (("REP-00303", 2),), ()),
)



async def cargar(sesion, contexto):
    ahora, usuarios = contexto["ahora"], contexto["usuarios"]
    repuestos, ubicaciones, fisico, movimientos = (contexto[k] for k in ("repuestos", "ubicaciones", "fisico", "movimientos"))
    for (
        estado, urgencia, origen, creo, asignado, resolvio, motivo, cancelacion, hace, items, recepciones
    ) in PEDIDOS_COMPRA:
        creado_en = ahora - hace
        pedido = PedidoCompraDb(
            creada_por_usuario_id=usuarios[creo],
            urgencia=urgencia,
            origen=origen,
            estado=estado,
            motivo=motivo,
            asignado_a_usuario_id=usuarios[asignado] if asignado else None,
            revision_resuelta_por_usuario_id=usuarios[resolvio] if resolvio else None,
            revision_resuelta_en=creado_en + timedelta(hours=4) if resolvio else None,
            motivo_cancelacion=cancelacion,
            creado_en=creado_en,
        )
        sesion.add(pedido)
        await sesion.flush()
        lineas = {}
        for repuesto, cantidad in items:
            linea = ItemPedidoCompraDb(
                pedido_compra_id=pedido.id, repuesto_id=repuestos[repuesto].id, cantidad_solicitada=cantidad
            )
            sesion.add(linea)
            lineas[repuesto] = linea
        await sesion.flush()
        for recibida_hace, recibido in recepciones:
            recepcion = RecepcionCompraDb(
                pedido_compra_id=pedido.id,
                recibida_por_usuario_id=usuarios["encargado"],
                recibida_en=ahora - recibida_hace,
            )
            sesion.add(recepcion)
            await sesion.flush()
            for repuesto, ubicacion, cantidad in recibido:
                item = ItemRecepcionCompraDb(
                    recepcion_id=recepcion.id,
                    item_pedido_compra_id=lineas[repuesto].id,
                    ubicacion_id=ubicaciones[ubicacion].id,
                    cantidad=cantidad,
                )
                sesion.add(item)
                await sesion.flush()
                fisico[repuesto, ubicacion] += cantidad
                movimientos.append(
                    MovimientoStockDb(
                        repuesto_id=repuestos[repuesto].id,
                        ubicacion_id=ubicaciones[ubicacion].id,
                        tipo_movimiento="entrada",
                        cantidad=cantidad,
                        variacion_fisica=cantidad,
                        variacion_reservada=0,
                        realizado_por_usuario_id=usuarios["encargado"],
                        ocurrido_en=recepcion.recibida_en,
                        motivo=f"Recepción del pedido de compra {pedido.id}.",
                        item_recepcion_compra_id=item.id,
                    )
                )

