from collections import defaultdict

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_models.catalogo import (
    RepuestoDb,
    RepuestoXUbicacionDb,
    UbicacionDb,
)
from db.db_models.compras import (
    ItemPedidoCompraDb,
    ItemRecepcionCompraDb,
    PedidoCompraDb,
    RecepcionCompraDb,
)
from db.db_models.fechas import fecha_actual
from db.db_models.stock import MovimientoStockDb


class RepositorioPedidosCompra:
    def __init__(self, sesion: AsyncSession):
        self.sesion = sesion

    async def obtener_pedido(self, pedido_id: int):
        return await self.sesion.get(PedidoCompraDb, pedido_id)

    async def obtener_repuesto(self, repuesto_id: int):
        return await self.sesion.get(RepuestoDb, repuesto_id)

    async def obtener_ubicacion(self, ubicacion_id: int):
        return await self.sesion.get(UbicacionDb, ubicacion_id)

    async def obtener_item_pedido(self, item_id: int):
        return await self.sesion.get(ItemPedidoCompraDb, item_id)

    async def listar(self, offset: int, limit: int, estado: str | None):
        filtros = [PedidoCompraDb.estado == estado] if estado else []

        total = await self.sesion.scalar(
            select(func.count())
            .select_from(PedidoCompraDb)
            .where(*filtros)
        )

        consulta = (
            select(PedidoCompraDb)
            .where(*filtros)
            .order_by(
                PedidoCompraDb.creado_en.desc(),
                PedidoCompraDb.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        pedidos = await self.sesion.scalars(consulta)
        return list(pedidos), total or 0

    async def items_por_pedido(self, pedido_ids: list[int]):
        resultado = defaultdict(list)

        if not pedido_ids:
            return resultado

        consulta = (
            select(ItemPedidoCompraDb, RepuestoDb)
            .join(
                RepuestoDb,
                RepuestoDb.id == ItemPedidoCompraDb.repuesto_id,
            )
            .where(ItemPedidoCompraDb.pedido_compra_id.in_(pedido_ids))
            .order_by(ItemPedidoCompraDb.id)
        )

        filas = (await self.sesion.execute(consulta)).all()

        for item, repuesto in filas:
            resultado[item.pedido_compra_id].append((item, repuesto))

        return resultado

    async def recepciones_por_pedido(self, pedido_ids: list[int]):
        resultado = defaultdict(list)

        if not pedido_ids:
            return resultado

        consulta = (
            select(RecepcionCompraDb)
            .where(RecepcionCompraDb.pedido_compra_id.in_(pedido_ids))
            .order_by(
                RecepcionCompraDb.recibida_en,
                RecepcionCompraDb.id,
            )
        )

        recepciones = await self.sesion.scalars(consulta)

        for recepcion in recepciones:
            resultado[recepcion.pedido_compra_id].append(recepcion)

        return resultado

    async def items_por_recepcion(self, recepcion_ids: list[int]):
        resultado = defaultdict(list)

        if not recepcion_ids:
            return resultado

        consulta = (
            select(ItemRecepcionCompraDb, UbicacionDb)
            .join(
                UbicacionDb,
                UbicacionDb.id == ItemRecepcionCompraDb.ubicacion_id,
            )
            .where(ItemRecepcionCompraDb.recepcion_id.in_(recepcion_ids))
            .order_by(ItemRecepcionCompraDb.id)
        )

        filas = (await self.sesion.execute(consulta)).all()

        for item, ubicacion in filas:
            resultado[item.recepcion_id].append((item, ubicacion))

        return resultado

    async def incrementar_stock(
        self,
        repuesto_id: int,
        ubicacion_id: int,
        cantidad: int,
    ) -> bool:
        existencia = RepuestoXUbicacionDb

        resultado = await self.sesion.execute(
            update(existencia)
            .where(
                existencia.repuesto_id == repuesto_id,
                existencia.ubicacion_id == ubicacion_id,
            )
            .values(
                cantidad_fisica=existencia.cantidad_fisica + cantidad,
                actualizado_en=fecha_actual(),
            )
            .execution_options(synchronize_session=False)
        )

        if resultado.rowcount == 1:
            return True

        actual = await self.sesion.get(
            RepuestoXUbicacionDb,
            (repuesto_id, ubicacion_id),
        )

        if actual is not None:
            return False

        self.sesion.add(
            RepuestoXUbicacionDb(
                repuesto_id=repuesto_id,
                ubicacion_id=ubicacion_id,
                cantidad_fisica=cantidad,
                cantidad_reservada=0,
                actualizado_en=fecha_actual(),
            )
        )

        await self.sesion.flush()
        return True

    async def guardar(self, entidad):
        self.sesion.add(entidad)
        await self.sesion.flush()
        await self.sesion.refresh(entidad)
        return entidad

    async def guardar_movimiento(self, movimiento: MovimientoStockDb):
        return await self.guardar(movimiento)