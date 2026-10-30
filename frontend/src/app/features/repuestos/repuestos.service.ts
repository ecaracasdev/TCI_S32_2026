import { Observable } from 'rxjs';
import { RepuestoDto } from './repuestos.models';

/**
 * Contrato de datos de las vistas de repuestos (T12).
 * Lo cumplen RepuestosHttpService (API real) y MockRepuestosService (fixtures).
 * Es una clase abstracta y no una interface porque Angular la usa como token de inyección.
 */
export abstract class RepuestosService {
  abstract listar(): Observable<RepuestoDto[]>;
  abstract obtener(id: number): Observable<RepuestoDto>;
}
