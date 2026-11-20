"""Consultas de persistencia de reparaciones, sus usos de repuestos e informes."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_models.catalogo import RepuestoDb, RepuestoXUbicacionDb
from db.db_models.fechas import fecha_actual
from db.db_models.incidencias import (
    IncidenciaDb,
    InformeResolucionDb,
    ReparacionDb,
    UsoRepuestoReparacionDb,
)


class RepositorioReparaciones:
    """Accede a reparaciones y existencias mediante la sesión de la solicitud."""

    def __init__(self, sesion: AsyncSession):
        self.sesion = sesion

    async def obtener_incidencia(self, incidencia_id: int):
        return await self.sesion.get(IncidenciaDb, incidencia_id)

    async def obtener_reparacion(self, reparacion_id: int):
        return await self.sesion.get(ReparacionDb, reparacion_id)

    async def reparacion_de_incidencia(self, incidencia_id: int):
        return await self.sesion.scalar(select(ReparacionDb).where(ReparacionDb.incidencia_id == incidencia_id))

    async def obtener_repuesto(self, repuesto_id: int):
        return await self.sesion.get(RepuestoDb, repuesto_id)

    async def existencias_del_repuesto(self, repuesto_id: int) -> list[RepuestoXUbicacionDb]:
        """Existencias del repuesto, la de mayor disponible primero."""
        existencia = RepuestoXUbicacionDb
        consulta = (
            select(existencia)
            .where(existencia.repuesto_id == repuesto_id)
            .order_by((existencia.cantidad_fisica - existencia.cantidad_reservada).desc(), existencia.ubicacion_id)
        )
        return list(await self.sesion.scalars(consulta))

    async def descontar(self, repuesto_id: int, ubicacion_id: int, cantidad: int) -> bool:
        """RN-01: descuenta del stock físico solo si el disponible (físico menos reservado) alcanza.

        Es una única sentencia condicionada: si dos usos compiten por las últimas unidades,
        la base aplica uno solo y el otro no modifica ninguna fila.
        """
        existencia = RepuestoXUbicacionDb
        resultado = await self.sesion.execute(
            update(existencia)
            .where(
                existencia.repuesto_id == repuesto_id,
                existencia.ubicacion_id == ubicacion_id,
                existencia.cantidad_fisica - existencia.cantidad_reservada >= cantidad,
            )
            .values(cantidad_fisica=existencia.cantidad_fisica - cantidad, actualizado_en=fecha_actual())
            .execution_options(synchronize_session=False)
        )
        return resultado.rowcount == 1

    async def uso_de(self, reparacion_id: int, repuesto_id: int):
        return await self.sesion.scalar(
            select(UsoRepuestoReparacionDb).where(
                UsoRepuestoReparacionDb.reparacion_id == reparacion_id,
                UsoRepuestoReparacionDb.repuesto_id == repuesto_id,
            )
        )

    async def usos_de(self, reparacion_id: int):
        """Líneas de uso de la reparación con su repuesto."""
        consulta = (
            select(UsoRepuestoReparacionDb, RepuestoDb)
            .join(RepuestoDb, RepuestoDb.id == UsoRepuestoReparacionDb.repuesto_id)
            .where(UsoRepuestoReparacionDb.reparacion_id == reparacion_id)
            .order_by(UsoRepuestoReparacionDb.id)
        )
        return (await self.sesion.execute(consulta)).all()

    async def informe_de(self, reparacion_id: int):
        return await self.sesion.scalar(
            select(InformeResolucionDb).where(InformeResolucionDb.reparacion_id == reparacion_id)
        )

    async def guardar(self, entidad):
        """Persiste los cambios dentro de la transacción de la solicitud."""
        self.sesion.add(entidad)
        await self.sesion.flush()
        await self.sesion.refresh(entidad)
        return entidad
