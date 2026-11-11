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
}