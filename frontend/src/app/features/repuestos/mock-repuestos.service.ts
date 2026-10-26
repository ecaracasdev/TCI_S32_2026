import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { Pagina, RepuestoDto } from './repuestos.models';
import { RepuestosService } from './repuestos.service';

@Injectable({ providedIn: 'root' })
export class MockRepuestosService extends RepuestosService {
  private readonly http = inject(HttpClient);

  listar(): Observable<RepuestoDto[]> {
    return this.http.get<Pagina<RepuestoDto>>('mock/repuestos.json').pipe(map((pagina) => pagina.items));
  }

  obtener(id: number): Observable<RepuestoDto> {
    return this.listar().pipe(
      map((items) => {
        const repuesto = items.find((item) => item.id === id);
        if (!repuesto) throw new Error(`Repuesto ${id} inexistente`);
        return repuesto;
      }),
    );
  }
}
