
from typing import Optional

from repositories.incidencias_repository import RepositorioIncidencias
from db.db_models.incidencias import IncidenciaDb
from models.incidencia_mdl import (
    IncidenciaResponseDto,
    FotoIncidenciaDto,
)
from models.catalogo_mdl import (
    MaquinaResponseDto,
    TipoMaquinaResumenDto,
)


class ServicioIncidencias:
    def __init__(self, repositorio: RepositorioIncidencias):
        self.repositorio = repositorio

    async def serializar(
        self, incidencia: IncidenciaDb
    ) -> IncidenciaResponseDto:
        maquina = await self.repositorio.obtener_maquina_por_id(
            incidencia.maquina_id
        )

        maquina_dto = None

        if maquina:
            tipo_maquina = (
                await self.repositorio.obtener_tipo_maquina_por_id(
                    maquina.tipo_maquina_id
                )
            )

            maquina_dto = MaquinaResponseDto.model_validate(
                {
                    "id": maquina.id,
                    "codigo": maquina.codigo,
                    "tipo_maquina_id": maquina.tipo_maquina_id,
                    "tipo_maquina": (
                        TipoMaquinaResumenDto.model_validate(
                            tipo_maquina,
                            from_attributes=True,
                        )
                        if tipo_maquina
                        else None
                    ),
                    "numero_serie": maquina.numero_serie,
                    "estado": maquina.estado,
                    "fecha_instalacion": maquina.fecha_instalacion,
                    "creado_en": maquina.creado_en,
                    "actualizado_en": maquina.actualizado_en,
                }
            )

        fotos = await self.repositorio.obtener_fotos_por_incidencia(
            incidencia.id
        )

        datos = {
            "id": incidencia.id,
            "maquina_id": incidencia.maquina_id,
            "maquina": maquina_dto,
            "reportada_por_usuario_id": incidencia.reportada_por_usuario_id,
            "descripcion": incidencia.descripcion,
            "estado": incidencia.estado,
            "turno": incidencia.turno,
            "reportada_en": incidencia.reportada_en,
            "resuelta_en": incidencia.resuelta_en,
            "reparacion_id": await self.repositorio.obtener_reparacion_id(incidencia.id),
            "fotos": [
                FotoIncidenciaDto.model_validate(
                    foto,
                    from_attributes=True,
                )
                for foto in fotos
            ],
        }

        return IncidenciaResponseDto.model_validate(datos)

    async def listar_incidencias(
        self, offset: int, limit: int, estado: Optional[str]
    ):
        items, total = await self.repositorio.listar(
            offset, limit, estado
        )

        items_serializados = [
            await self.serializar(item) for item in items
        ]

        return {
            "items": items_serializados,
            "total": total,
            "offset": offset,
            "limit": limit,
        }
