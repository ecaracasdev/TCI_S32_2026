import { Observable } from 'rxjs';
import { MaquinaDto } from './maquinas.models';

export abstract class MaquinasService {
  abstract listar(): Observable<MaquinaDto[]>;
  abstract obtenerPorId(id: number): Observable<MaquinaDto>;
}
