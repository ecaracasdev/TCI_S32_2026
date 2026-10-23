import { Observable } from 'rxjs';
import { AlertaStockDto, IncidenciaDto } from './inicio.models';

/**
 * Contrato de datos de la vista de inicio (T11).
 * Lo cumplen InicioHttpService y MockInicioService.
 */
export abstract class InicioService {
  abstract incidenciasRecientes(): Observable<IncidenciaDto[]>;
  abstract alertasStock(): Observable<AlertaStockDto[]>;
}