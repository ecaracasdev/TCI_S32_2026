import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, delay, map } from 'rxjs';
import { IncidenciaCreateDto, IncidenciaResponseDto } from './reportar-incidencia.models';
import { ReportarIncidenciaService } from './reportar-incidencia.service';

@Injectable({ providedIn: 'root' })
export class MockReportarIncidenciaService extends ReportarIncidenciaService {
  private readonly http = inject(HttpClient);

  crearIncidencia(incidencia: IncidenciaCreateDto): Observable<IncidenciaResponseDto> {
    return this.http
      .get<{ items: { codigo: string }[] }>('mock/maquinas.json')
      .pipe(
        delay(800),
        map((pagina) => {
          const existe = pagina.items.some((maquina) => maquina.codigo === incidencia.maquina_codigo);
          if (!existe) {
            throw new Error('No existe una máquina con ese código');
          }

          return {
            id: Date.now(),
            descripcion: incidencia.descripcion,
            estado: 'reportada',
            turno: incidencia.turno,
            reportada_en: new Date().toISOString(),
          };
        }),
      );
  }
}
