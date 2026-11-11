import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';

import { ComprasService } from './compras.service';

import {
  Pagina,
  RepuestoDto,
} from '../repuestos/repuestos.models';

@Injectable({ providedIn: 'root' })
export class MockComprasService extends ComprasService {

  private readonly http = inject(HttpClient);

  listar(): Observable<RepuestoDto[]> {

    return this.http
      .get<Pagina<RepuestoDto>>(
        'mock/repuestos.json',
      )
      .pipe(
        map(
          (pagina) => pagina.items,
        ),
      );
  }
}