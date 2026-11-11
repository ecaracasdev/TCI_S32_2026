import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';

import { ConsultaIncidenciasService } from './consulta-incidencias.service';

import {
  IncidenciaDto,
  Pagina,
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
}