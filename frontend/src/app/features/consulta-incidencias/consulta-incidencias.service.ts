import { Observable } from 'rxjs';
import { IncidenciaDto } from './consulta-incidencias.models';

export abstract class ConsultaIncidenciasService {

  abstract listar(): Observable<IncidenciaDto[]>;

  abstract obtenerPorId(
    id: number,
  ): Observable<IncidenciaDto>;

}