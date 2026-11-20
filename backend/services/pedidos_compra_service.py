
from collections import defaultdict

from db.db_models.compras import (
    ItemPedidoCompraDb,
    ItemRecepcionCompraDb,
    PedidoCompraDb,
    RecepcionCompraDb,
)
from db.db_models.fechas import fecha_actual
from db.db_models.stock import MovimientoStockDb
from models.compra_mdl import (
    PedidoCompraResponseDto,
    RecepcionCompraResponseDto,
)
from repositories.pedidos_compra_repository import RepositorioPedidosCompra


class ErrorPedidoCompra(Exception):
    def __init__(self, codigo_http: int, codigo: str, mensaje: str):
        super().__init__(mensaje)
        self.codigo_http = codigo_http
        self.codigo = codigo
        self.mensaje = mensaje


class ServicioPedidosCompra:
    def __init__(self, repositorio: RepositorioPedidosCompra):
        self.repositorio = repositorio

    async def serializar_recepciones(self, recepciones: list[RecepcionCompraDb]):
        agrupados = await self.repositorio.items_por_recepcion(
            [recepcion.id for recepcion in recepciones]
        )
        return [
            RecepcionCompraResponseDto.model_validate(
                {
                    **recepcion.model_dump(),
                    "items": [
                        {**item.model_dump(), "ubicacion": ubicacion}
                        for item, ubicacion in agrupados[recepcion.id]
                    ],
                }
            )
            for recepcion in recepciones
        ]

    async def serializar(self, pedidos: list[PedidoCompraDb]):
        if not pedidos:
            return []

        ids = [pedido.id for pedido in pedidos]
        partidas = await self.repositorio.items_por_pedido(ids)
        recepciones = await self.repositorio.recepciones_por_pedido(ids)
        resultado = []

        for pedido in pedidos:
            recepciones_dto = await self.serializar_recepciones(
                recepciones[pedido.id]
            )
            datos = {
                **pedido.model_dump(),
                "items": [
                    {**item.model_dump(), "repuesto": repuesto}
                    for item, repuesto in partidas[pedido.id]
                ],
                "recepciones": recepciones_dto,
            }
            resultado.append(PedidoCompraResponseDto.model_validate(datos))

        return resultado

    async def listar(self, offset, limit, estado):
        pedidos, total = await self.repositorio.listar(offset, limit, estado)
        return {
            "items": await self.serializar(pedidos),
            "total": total,
            "offset": offset,
            "limit": limit,
        }

    async def obtener(self, pedido_id):
        pedido = await self.repositorio.obtener_pedido(pedido_id)

        if pedido is None:
            raise ErrorPedidoCompra(
                404,
                "pedido_compra_inexistente",
                "Pedido de compra inexistente.",
            )

        return (await self.serializar([pedido]))[0]

    async def crear(self, datos, usuario_id):
        partidas = datos["items"]
        repuestos = [partida["repuesto_id"] for partida in partidas]

        if len(repuestos) != len(set(repuestos)):
            raise ErrorPedidoCompra(
                422,
                "partida_duplicada",
                "No se puede repetir un repuesto en el mismo pedido.",
            )

        for partida in partidas:
            if (
                await self.repositorio.obtener_repuesto(
                    partida["repuesto_id"]
                )
                is None
            ):
                raise ErrorPedidoCompra(
                    404,
                    "repuesto_inexistente",
                    "Uno de los repuestos indicados no existe.",
                )

        pedido = await self.repositorio.guardar(
            PedidoCompraDb(
                creada_por_usuario_id=usuario_id,
                urgencia=datos.get("urgencia", "normal"),
                origen="manual",
                estado="creado",
                motivo=datos.get("motivo"),
            )
        )

        for partida in partidas:
            await self.repositorio.guardar(
                ItemPedidoCompraDb(
                    pedido_compra_id=pedido.id,
                    repuesto_id=partida["repuesto_id"],
                    cantidad_solicitada=partida["cantidad_solicitada"],
                )
            )

        return (await self.serializar([pedido]))[0]

    async def asignar(self, pedido, datos):
        if pedido.estado != "creado":
            raise ErrorPedidoCompra(
                409,
                "estado_pedido_invalido",
                "Solo se pueden asignar pedidos en estado creado.",
            )

        pedido.asignado_a_usuario_id = datos["asignado_a_usuario_id"]
        pedido.estado = "pendiente_revision"
        pedido = await self.repositorio.guardar(pedido)

        return (await self.serializar([pedido]))[0]

    async def revisar(self, pedido, datos, usuario_id):
        if pedido.estado != "pendiente_revision":
            raise ErrorPedidoCompra(
                409,
                "estado_pedido_invalido",
                "El pedido no está pendiente de revisión.",
            )

        pedido.revision_resuelta_por_usuario_id = usuario_id
        pedido.revision_resuelta_en = fecha_actual()
        pedido.estado = "pendiente_aprobacion"

        if datos.get("observaciones"):
            pedido.motivo = (
                f"{pedido.motivo or ''}\n{datos['observaciones']}"
            ).strip()

        pedido = await self.repositorio.guardar(pedido)

        return (await self.serializar([pedido]))[0]

    async def aprobar(self, pedido, datos, usuario_id):
        if pedido.estado != "pendiente_aprobacion":
            raise ErrorPedidoCompra(
                409,
                "estado_pedido_invalido",
                "Solo se pueden aprobar pedidos pendientes de aprobación.",
            )

        if datos.get("observaciones"):
            pedido.motivo = (
                f"{pedido.motivo or ''}\n{datos['observaciones']}"
            ).strip()

        pedido.revision_resuelta_por_usuario_id = usuario_id
        pedido.revision_resuelta_en = fecha_actual()
        pedido.estado = "confirmado"
        pedido = await self.repositorio.guardar(pedido)

        return (await self.serializar([pedido]))[0]

    async def cancelar(self, pedido, datos):
        if pedido.estado != "pendiente_aprobacion":
            raise ErrorPedidoCompra(
                409,
                "estado_pedido_invalido",
                "Solo se pueden cancelar pedidos pendientes de aprobación.",
            )

        pedido.estado = "cancelado"
        pedido.motivo_cancelacion = datos["motivo"]
        pedido = await self.repositorio.guardar(pedido)

        return (await self.serializar([pedido]))[0]

    async def confirmar(self, pedido):
        if pedido.estado != "confirmado":
            raise ErrorPedidoCompra(
                409,
                "estado_pedido_invalido",
                "Solo se pueden confirmar pedidos aprobados.",
            )

        pedido.estado = "pendiente_recepcion"
        pedido = await self.repositorio.guardar(pedido)

        return (await self.serializar([pedido]))[0]

    async def recibir(self, pedido, datos, usuario_id):
        if pedido.estado not in ("confirmado", "pendiente_recepcion"):
            raise ErrorPedidoCompra(
                409,
                "estado_pedido_invalido",
                "Solo se pueden recibir pedidos confirmados o pendientes de recepción.",
            )

        partidas = (
            await self.repositorio.items_por_pedido([pedido.id])
        )[pedido.id]
        items_pedido = {item.id: item for item, _ in partidas}

        cantidades_recibidas = defaultdict(int)
        recepciones_previas = (
            await self.repositorio.recepciones_por_pedido([pedido.id])
        )[pedido.id]

        for recepcion_previa in recepciones_previas:
            items_previos = (
                await self.repositorio.items_por_recepcion(
                    [recepcion_previa.id]
                )
            )[recepcion_previa.id]

            for item_previo, _ in items_previos:
                cantidades_recibidas[
                    item_previo.item_pedido_compra_id
                ] += item_previo.cantidad

        cantidades_nuevas = defaultdict(int)
        claves = set()

        for partida in datos["items"]:
            item_id = partida["item_pedido_compra_id"]
            ubicacion_id = partida["ubicacion_id"]
            cantidad = partida["cantidad"]
            clave = (item_id, ubicacion_id)

            if clave in claves:
                raise ErrorPedidoCompra(
                    422,
                    "partida_duplicada",
                    "No se puede repetir una partida para la misma ubicación.",
                )

            claves.add(clave)

            if item_id not in items_pedido:
                raise ErrorPedidoCompra(
                    404,
                    "partida_inexistente",
                    "La partida no pertenece al pedido indicado.",
                )

            ubicacion = await self.repositorio.obtener_ubicacion(
                ubicacion_id
            )

            if ubicacion is None or not ubicacion.activo:
                raise ErrorPedidoCompra(
                    404,
                    "ubicacion_inexistente",
                    "La ubicación indicada no existe o está inactiva.",
                )

            cantidades_nuevas[item_id] += cantidad

        for item_id, cantidad in cantidades_nuevas.items():
            solicitado = items_pedido[item_id].cantidad_solicitada
            recibido = cantidades_recibidas[item_id]

            if recibido + cantidad > solicitado:
                raise ErrorPedidoCompra(
                    409,
                    "recepcion_excedida",
                    "La cantidad recibida supera la cantidad solicitada.",
                )

        recepcion = await self.repositorio.guardar(
            RecepcionCompraDb(
                pedido_compra_id=pedido.id,
                recibida_por_usuario_id=usuario_id,
                delegada_a_usuario_id=datos.get("delegada_a_usuario_id"),
                notas=datos.get("notas"),
            )
        )

        for partida in datos["items"]:
            item_pedido = items_pedido[
                partida["item_pedido_compra_id"]
            ]
            ubicacion_id = partida["ubicacion_id"]
            cantidad = partida["cantidad"]

            item_recepcion = await self.repositorio.guardar(
                ItemRecepcionCompraDb(
                    recepcion_id=recepcion.id,
                    item_pedido_compra_id=item_pedido.id,
                    ubicacion_id=ubicacion_id,
                    cantidad=cantidad,
                )
            )

            actualizado = await self.repositorio.incrementar_stock(
                item_pedido.repuesto_id,
                ubicacion_id,
                cantidad,
            )

            if not actualizado:
                raise ErrorPedidoCompra(
                    409,
                    "existencia_inconsistente",
                    "No se pudo actualizar la existencia del repuesto.",
                )

            await self.repositorio.guardar_movimiento(
                MovimientoStockDb(
                    repuesto_id=item_pedido.repuesto_id,
                    ubicacion_id=ubicacion_id,
                    tipo_movimiento="recepcion_compra",
                    cantidad=cantidad,
                    variacion_fisica=cantidad,
                    variacion_reservada=0,
                    realizado_por_usuario_id=usuario_id,
                    motivo=f"Recepción del pedido de compra {pedido.id}.",
                    item_recepcion_compra_id=item_recepcion.id,
                )
            )

        completas = all(
            cantidades_recibidas[item.id]
            + cantidades_nuevas[item.id]
            == item.cantidad_solicitada
            for item in items_pedido.values()
        )

        if completas:
            pedido.estado = "recibido"
        else:
            pedido.estado = "pendiente_recepcion"

        await self.repositorio.guardar(pedido)

        recepcion_actual = (
            await self.repositorio.items_por_recepcion([recepcion.id])
        )[recepcion.id]

        return RecepcionCompraResponseDto.model_validate(
            {
                **recepcion.model_dump(),
                "items": [
                    {
                        **item.model_dump(),
                        "ubicacion": ubicacion,
                    }
                    for item, ubicacion in recepcion_actual
                ],
            }
        )
