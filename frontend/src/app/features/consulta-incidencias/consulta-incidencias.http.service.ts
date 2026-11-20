import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';

import { environment } from '../../../environments/environment';

import {
  ConsultaIncidenciasService,
} from './consulta-incidencias.service';

import {
  IncidenciaDto,
  Pagina,
  ReparacionDto,
} from './consulta-incidencias.models';

@Injectable({ providedIn: 'root' })
export class ConsultaIncidenciasHttpService
  extends ConsultaIncidenciasService {

  private readonly http = inject(HttpClient);

  listar(): Observable<IncidenciaDto[]> {
    return this.http
      .get<Pagina<IncidenciaDto>>(
        `${environment.apiUrl}/api/v0/incidencias`,
      )
      .pipe(
        map((pagina) => pagina.items),
      );
  }

  obtenerPorId(
    id: number,
  ): Observable<IncidenciaDto> {

    return this.http.get<IncidenciaDto>(
      `${environment.apiUrl}/api/v0/incidencias/${id}`,
    );
  }

  tomar(incidenciaId: number): Observable<ReparacionDto> {
    return this.http.post<ReparacionDto>(
      `${environment.apiUrl}/api/v0/incidencias/${incidenciaId}/reparacion`,
      {},
    );
  }

  obtenerReparacion(id: number): Observable<ReparacionDto> {
    return this.http.get<ReparacionDto>(
      `${environment.apiUrl}/api/v0/reparaciones/${id}`,
    );
  }

  finalizar(reparacionId: number, resumen: string): Observable<unknown> {
    return this.http.post(
      `${environment.apiUrl}/api/v0/reparaciones/${reparacionId}/informe`,
      { resumen },
    );
  }
}
