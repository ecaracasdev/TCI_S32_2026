import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { IncidenciaCreateDto, IncidenciaResponseDto } from './reportar-incidencia.models';
import { ReportarIncidenciaService } from './reportar-incidencia.service';
import { environment } from 'src/environments/environment';

@Injectable({
    providedIn: 'root',
})
export class ReportarIncidenciaHttpService extends ReportarIncidenciaService {
    private readonly http = inject(HttpClient);
    crearIncidencia(incidencia: IncidenciaCreateDto): Observable<IncidenciaResponseDto> {
        return this.http.post<IncidenciaResponseDto>(
            `${environment.apiUrl}/api/v0/incidencias`,
            incidencia,
        );
    }
}
