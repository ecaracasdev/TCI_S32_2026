import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { MaquinaDto, Pagina } from './maquinas.models';
import { MaquinasService } from './maquinas.service';

@Injectable({ providedIn: 'root' })
export class MockMaquinasService extends MaquinasService {
  private readonly http = inject(HttpClient);
  private readonly fixture = 'mock/maquinas.json';

  listar(): Observable<MaquinaDto[]> {
    return this.http.get<Pagina<MaquinaDto>>(this.fixture).pipe(map((pagina) => pagina.items));
  }

  obtenerPorId(id: number): Observable<MaquinaDto> {
    return this.http.get<Pagina<MaquinaDto>>(this.fixture).pipe(
      map((pagina) => {
        const maquina = pagina.items.find((item) => item.id === id);
        if (!maquina) throw new Error(`No existe la máquina ${id}`);
        return maquina;
      }),
    );
  }
}
