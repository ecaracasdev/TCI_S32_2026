from typing import Optional, Tuple, Sequence

from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_models.incidencias import IncidenciaDb, FotoIncidenciaDb, ReparacionDb
from db.db_models.catalogo import MaquinaDb, TipoMaquinaDb


class RepositorioIncidencias:
    def __init__(self, sesion: AsyncSession):
        self.sesion = sesion

    async def obtener(self, modelo, id_recurso: int):
        return await self.sesion.get(modelo, id_recurso)

    async def obtener_maquina_por_codigo(
        self, codigo: str
    ) -> Optional[MaquinaDb]:
        resultado = await self.sesion.execute(
            select(MaquinaDb).where(MaquinaDb.codigo == codigo)
        )
        return resultado.scalars().first()

    async def obtener_maquina_por_id(
        self, maquina_id: int
    ) -> Optional[MaquinaDb]:
        resultado = await self.sesion.execute(
            select(MaquinaDb).where(MaquinaDb.id == maquina_id)
        )
        return resultado.scalars().first()

    async def obtener_tipo_maquina_por_id(self, tipo_maquina_id: int):
        resultado = await self.sesion.execute(
            select(TipoMaquinaDb).where(
                TipoMaquinaDb.id == tipo_maquina_id
            )
        )
        return resultado.scalars().first()

    async def obtener_fotos_por_incidencia(
        self, incidencia_id: int
    ) -> Sequence[FotoIncidenciaDb]:
        resultado = await self.sesion.execute(
            select(FotoIncidenciaDb).where(
                FotoIncidenciaDb.incidencia_id == incidencia_id
            )
        )
        return resultado.scalars().all()

    async def guardar(
        self, incidencia: IncidenciaDb, fotos_data: list
    ) -> IncidenciaDb:
        self.sesion.add(incidencia)
        await self.sesion.flush()

        for foto in fotos_data:
            db_foto = FotoIncidenciaDb(
                incidencia_id=incidencia.id,
                contenido_base64=foto.contenido_base64,
                nombre_archivo=foto.nombre_archivo,
                tipo_mime=foto.tipo_mime,
                capturada_en=foto.capturada_en,
            )
            self.sesion.add(db_foto)

        await self.sesion.commit()
        await self.sesion.refresh(incidencia)
        return incidencia

    async def obtener_reparacion_id(self, incidencia_id: int) -> Optional[int]:
        """Id de la reparación de la incidencia, si un empleado ya la tomó."""
        return await self.sesion.scalar(
            select(ReparacionDb.id).where(ReparacionDb.incidencia_id == incidencia_id)
        )

    async def listar(
        self, offset: int, limit: int, estado: Optional[str]
    ) -> Tuple[Sequence[IncidenciaDb], int]:
        query = select(IncidenciaDb)
        count_query = select(func.count()).select_from(IncidenciaDb)

        if estado:
            query = query.where(IncidenciaDb.estado == estado)
            count_query = count_query.where(
                IncidenciaDb.estado == estado
            )

        total_result = await self.sesion.execute(count_query)
        total = total_result.scalar_one()

        # Las más recientes primero, para que la paginación sea estable.
        query = query.order_by(IncidenciaDb.reportada_en.desc(), IncidenciaDb.id.desc()).offset(offset).limit(limit)
        resultado = await self.sesion.execute(query)
        items = resultado.scalars().all()

        return items, total
