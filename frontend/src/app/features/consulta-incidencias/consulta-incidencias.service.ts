import { Observable } from 'rxjs';
import { IncidenciaDto, ReparacionDto } from './consulta-incidencias.models';

export abstract class ConsultaIncidenciasService {

  abstract listar(): Observable<IncidenciaDto[]>;

  abstract obtenerPorId(
    id: number,
  ): Observable<IncidenciaDto>;

  /** CUN-01: el empleado toma la incidencia y se crea su reparación. */
  abstract tomar(incidenciaId: number): Observable<ReparacionDto>;

  abstract obtenerReparacion(id: number): Observable<ReparacionDto>;

  /** Registra el informe de resolución: la incidencia queda resuelta. */
  abstract finalizar(reparacionId: number, resumen: string): Observable<unknown>;

}
