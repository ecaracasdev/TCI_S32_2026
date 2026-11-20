"""CUN-01: el empleado toma una incidencia, registra los repuestos usados y la resuelve.

Sigue la máquina de estados T01: reportada (o en triage) → en reparación → resuelta.
Cada uso descuenta stock con una sentencia condicionada (RN-01) y deja un movimiento
de stock (RN-06); el umbral (RN-02) lo evalúa la consulta de alertas.
"""

from db.db_models.fechas import fecha_actual
from db.db_models.incidencias import (
    IncidenciaDb,
    InformeResolucionDb,
    ReparacionDb,
    UsoRepuestoReparacionDb,
)
from db.db_models.stock import MovimientoStockDb
from models.incidencia_mdl import (
    InformeResolucionResponseDto,
    ReparacionResponseDto,
    UsoRepuestoResponseDto,
)
from repositories.reparaciones_repository import RepositorioReparaciones

ESTADOS_PARA_TOMAR = ("reportada", "en_triage")
EN_CURSO, COMPLETADA = "en_curso", "completada"


class ErrorReparacion(Exception):
    """Rechazo de una operación con el código HTTP y el código de error del contrato."""

    def __init__(self, codigo_http: int, codigo: str, mensaje: str):
        super().__init__(mensaje)
        self.codigo_http = codigo_http
        self.codigo = codigo
        self.mensaje = mensaje


class ServicioReparaciones:
    """Coordina la toma, el registro de usos y la resolución de una reparación."""

    def __init__(self, repositorio: RepositorioReparaciones):
        self.repositorio = repositorio

    def _uso(self, uso: UsoRepuestoReparacionDb, repuesto) -> UsoRepuestoResponseDto:
        return UsoRepuestoResponseDto.model_validate({**uso.model_dump(), "repuesto": repuesto})

    async def serializar(self, reparacion: ReparacionDb) -> ReparacionResponseDto:
        """Anida a la reparación sus usos de repuestos y su informe, si lo tiene."""
        usos = await self.repositorio.usos_de(reparacion.id)
        informe = await self.repositorio.informe_de(reparacion.id)
        return ReparacionResponseDto.model_validate(
            {
                **reparacion.model_dump(),
                "usos": [self._uso(uso, repuesto) for uso, repuesto in usos],
                "informe_resolucion": informe,
            }
        )

    async def tomar(self, incidencia: IncidenciaDb, usuario_id: int) -> ReparacionResponseDto:
        """El empleado toma la incidencia: crea la reparación y la incidencia pasa a en reparación."""
        if await self.repositorio.reparacion_de_incidencia(incidencia.id) is not None:
            raise ErrorReparacion(409, "incidencia_ya_tomada", "La incidencia ya tiene una reparación.")
        if incidencia.estado not in ESTADOS_PARA_TOMAR:
            raise ErrorReparacion(
                409, "estado_invalido", f"La incidencia está {incidencia.estado}; solo se toman incidencias reportadas o en triage."
            )
        reparacion = await self.repositorio.guardar(
            ReparacionDb(
                incidencia_id=incidencia.id,
                empleado_id=usuario_id,
                estado=EN_CURSO,
                iniciada_en=fecha_actual(),
            )
        )
        incidencia.estado = "en_reparacion"
        await self.repositorio.guardar(incidencia)
        return await self.serializar(reparacion)

    def _exigir_en_curso(self, reparacion: ReparacionDb) -> None:
        if reparacion.estado != EN_CURSO:
            raise ErrorReparacion(
                409, "reparacion_no_en_curso", f"La reparación está {reparacion.estado}; solo se opera sobre reparaciones en curso."
            )

    async def registrar_uso(self, reparacion: ReparacionDb, datos: dict, usuario_id: int) -> UsoRepuestoResponseDto:
        """RN-01: descuenta del stock la cantidad usada y la registra en la reparación."""
        self._exigir_en_curso(reparacion)
        repuesto = await self.repositorio.obtener_repuesto(datos["repuesto_id"])
        if repuesto is None:
            raise ErrorReparacion(404, "repuesto_inexistente", "Repuesto inexistente.")
        cantidad = datos["cantidad"]

        existencias = await self.repositorio.existencias_del_repuesto(repuesto.id)
        disponible = sum(e.cantidad_fisica - e.cantidad_reservada for e in existencias)
        if datos.get("ubicacion_id") is not None:
            ubicacion_id = datos["ubicacion_id"]
        elif existencias:
            ubicacion_id = existencias[0].ubicacion_id
        else:
            ubicacion_id = None
        if ubicacion_id is None or not await self.repositorio.descontar(repuesto.id, ubicacion_id, cantidad):
            raise ErrorReparacion(
                409,
                "stock_insuficiente",
                f"No hay stock disponible suficiente de {repuesto.codigo}: se piden {cantidad} y hay {disponible} disponibles"
                " (en una sola ubicación).",
            )

        uso = await self.repositorio.uso_de(reparacion.id, repuesto.id)
        if uso is None:
            uso = UsoRepuestoReparacionDb(
                reparacion_id=reparacion.id, repuesto_id=repuesto.id, cantidad=cantidad, usada_por_usuario_id=usuario_id
            )
        else:
            uso.cantidad += cantidad
        uso = await self.repositorio.guardar(uso)
        await self.repositorio.guardar(
            MovimientoStockDb(
                repuesto_id=repuesto.id,
                ubicacion_id=ubicacion_id,
                tipo_movimiento="consumo",
                cantidad=cantidad,
                variacion_fisica=-cantidad,
                variacion_reservada=0,
                realizado_por_usuario_id=usuario_id,
                motivo=f"Uso en la reparación {reparacion.id} (incidencia {reparacion.incidencia_id}).",
                uso_repuesto_reparacion_id=uso.id,
            )
        )
        return self._uso(uso, repuesto)

    async def finalizar(self, reparacion: ReparacionDb, resumen: str, usuario_id: int) -> InformeResolucionResponseDto:
        """Registra el informe: la reparación queda completada y la incidencia resuelta."""
        self._exigir_en_curso(reparacion)
        ahora = fecha_actual()
        informe = await self.repositorio.guardar(
            InformeResolucionDb(reparacion_id=reparacion.id, empleado_id=usuario_id, resumen=resumen)
        )
        reparacion.estado = COMPLETADA
        reparacion.completada_en = ahora
        await self.repositorio.guardar(reparacion)
        incidencia = await self.repositorio.obtener_incidencia(reparacion.incidencia_id)
        incidencia.estado = "resuelta"
        incidencia.resuelta_en = ahora
        await self.repositorio.guardar(incidencia)
        return InformeResolucionResponseDto.model_validate(informe)
