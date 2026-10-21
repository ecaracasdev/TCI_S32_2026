import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  AlertaStockDto,
  IncidenciaDto,
  LIMITE_RESUMEN,
  Pagina,
  masRecientes,
} from './inicio.models';
import { InicioService } from './inicio.service';

@Injectable({ providedIn: 'root' })
export class InicioHttpService extends InicioService {
  private readonly http = inject(HttpClient);

  incidenciasRecientes(): Observable<IncidenciaDto[]> {
    return this.http
      .get<Pagina<IncidenciaDto>>(`${environment.apiUrl}/api/v0/incidencias`)
      .pipe(map((pagina) => masRecientes(pagina.items)));
  }

  alertasStock(): Observable<AlertaStockDto[]> {
    const params = new HttpParams().set('limit', LIMITE_RESUMEN);
    return this.http
      .get<Pagina<AlertaStockDto>>(`${environment.apiUrl}/api/v0/stock/alertas`, { params })
      .pipe(map((pagina) => pagina.items));
  }
}