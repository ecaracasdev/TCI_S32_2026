import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ComprasService } from './compras.service';

import { RepuestoDto } from '../repuestos/repuestos.models';

import { RepuestosHttpService } from '../repuestos/repuestos.http.service';

@Injectable({ providedIn: 'root' })
export class ComprasHttpService extends ComprasService {

  constructor(
    private readonly repuestosService: RepuestosHttpService,
  ) {
    super();
  }

  listar(): Observable<RepuestoDto[]> {
    return this.repuestosService.listar();
  }
}