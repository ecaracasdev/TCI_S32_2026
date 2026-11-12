import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { MaquinaDto, Pagina } from './maquinas.models';
import { MaquinasService } from './maquinas.service';

@Injectable({ providedIn: 'root' })
export class MaquinasHttpService extends MaquinasService {
  private readonly http = inject(HttpClient);
  private readonly url = `${environment.apiUrl}/api/v0/maquinas`;

  listar(): Observable<MaquinaDto[]> {
    const params = new HttpParams().set('limit', 100);
    return this.http
      .get<Pagina<MaquinaDto>>(this.url, { params })
      .pipe(map((pagina) => pagina.items));
  }

  obtenerPorId(id: number): Observable<MaquinaDto> {
    return this.http.get<MaquinaDto>(`${this.url}/${id}`);
  }
}
