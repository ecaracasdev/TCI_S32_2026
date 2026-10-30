import { Observable } from 'rxjs';
import { IncidenciaCreateDto, IncidenciaResponseDto } from './reportar-incidencia.models';

export abstract class ReportarIncidenciaService {
    abstract crearIncidencia(incidencia: IncidenciaCreateDto): Observable<IncidenciaResponseDto>;
}
