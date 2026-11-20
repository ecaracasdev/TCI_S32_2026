import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map, throwError } from 'rxjs';

import { ConsultaIncidenciasService } from './consulta-incidencias.service';

import {
  IncidenciaDto,
  Pagina,
  ReparacionDto,
} from './consulta-incidencias.models';

@Injectable({ providedIn: 'root' })
export class MockConsultaIncidenciasService
  extends ConsultaIncidenciasService {

  private readonly http = inject(HttpClient);

  listar(): Observable<IncidenciaDto[]> {
    return this.http
      .get<Pagina<IncidenciaDto>>(
        'mock/incidencias.json',
      )
      .pipe(
        map((pagina) => pagina.items),
      );
  }

  obtenerPorId(
    id: number,
  ): Observable<IncidenciaDto> {

    return this.http
      .get<Pagina<IncidenciaDto>>(
        'mock/incidencias.json',
      )
      .pipe(
        map(
          (pagina) =>
            pagina.items.find(
              (i) => i.id === id,
            )!,
        ),
      );
  }

  /** En modo demostración no hay reparaciones: estas acciones necesitan el backend real. */
  tomar(): Observable<ReparacionDto> {
    return throwError(() => new Error('No disponible en modo demostración.'));
  }

  obtenerReparacion(): Observable<ReparacionDto> {
    return throwError(() => new Error('No disponible en modo demostración.'));
  }

  finalizar(): Observable<unknown> {
    return throwError(() => new Error('No disponible en modo demostración.'));
  }
}
