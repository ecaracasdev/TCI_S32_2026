import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  ReparacionDto,
  RepuestoDto,
  UsoRepuestoCreateDto,
  UsoRepuestoResponseDto,
} from './registrar-uso.models';
import { RegistrarUsoService } from './registrar-uso.service';

@Injectable({ providedIn: 'root' })
export class RegistrarUsoHttpService extends RegistrarUsoService {
  private readonly http = inject(HttpClient);

  buscarRepuesto(codigo: string): Observable<RepuestoDto> {
    return this.http.get<RepuestoDto>(
      `${environment.apiUrl}/api/v0/repuestos/codigo/${codigo}`,
    );
  }

  buscarReparacion(id: number): Observable<ReparacionDto> {
    return this.http.get<ReparacionDto>(
      `${environment.apiUrl}/api/v0/reparaciones/${id}`,
    );
  }

  registrarUso(
    reparacionId: number,
    datos: UsoRepuestoCreateDto,
  ): Observable<UsoRepuestoResponseDto> {
    return this.http.post<UsoRepuestoResponseDto>(
      `${environment.apiUrl}/api/v0/reparaciones/${reparacionId}/usos`,
      datos,
    );
  }
}
