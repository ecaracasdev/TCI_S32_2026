import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { LIMITE_LISTADO, Pagina, RepuestoDto } from './repuestos.models';
import { RepuestosService } from './repuestos.service';

@Injectable({ providedIn: 'root' })
export class RepuestosHttpService extends RepuestosService {
  private readonly http = inject(HttpClient);

  listar(): Observable<RepuestoDto[]> {
    const params = new HttpParams().set('limit', LIMITE_LISTADO);
    return this.http
      .get<Pagina<RepuestoDto>>(`${environment.apiUrl}/api/v0/repuestos`, { params })
      .pipe(map((pagina) => pagina.items));
  }

  obtener(id: number): Observable<RepuestoDto> {
    return this.http.get<RepuestoDto>(`${environment.apiUrl}/api/v0/repuestos/${id}`);
  }
}
