import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import {
  AlertaStockDto,
  IncidenciaDto,
  LIMITE_RESUMEN,
  Pagina,
  masRecientes,
} from './inicio.models';
import { InicioService } from './inicio.service';

/**
 * Implementación de demostración: lee los fixtures de public/mock/, que respetan
 * docs/spec/openapi-v0.json. Se usa cuando environment.useMockData es true.
 */
@Injectable({ providedIn: 'root' })
export class MockInicioService extends InicioService {
  private readonly http = inject(HttpClient);

  incidenciasRecientes(): Observable<IncidenciaDto[]> {
    return this.http
      .get<Pagina<IncidenciaDto>>('mock/incidencias.json')
      .pipe(map((pagina) => masRecientes(pagina.items)));
  }

  alertasStock(): Observable<AlertaStockDto[]> {
    return this.http
      .get<Pagina<AlertaStockDto>>('mock/stock-alertas.json')
      .pipe(map((pagina) => pagina.items.slice(0, LIMITE_RESUMEN)));
  }
}