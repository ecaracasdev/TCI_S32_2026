import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, delay, map, of, switchMap, tap } from 'rxjs';
import {
  ReparacionDto,
  RepuestoDto,
  UsoRepuestoCreateDto,
  UsoRepuestoResponseDto,
} from './registrar-uso.models';
import { RegistrarUsoService } from './registrar-uso.service';

@Injectable({ providedIn: 'root' })
export class MockRegistrarUsoService extends RegistrarUsoService {
  private readonly http = inject(HttpClient);
  private repuestos: RepuestoDto[] | null = null;

  private cargarRepuestos(): Observable<RepuestoDto[]> {
    if (this.repuestos) {
      return of(this.repuestos);
    }
    return this.http.get<{ items: RepuestoDto[] }>('mock/repuestos.json').pipe(
      map((pagina) => pagina.items),
      tap((items) => (this.repuestos = items)),
    );
  }

  buscarRepuesto(codigo: string): Observable<RepuestoDto> {
    return this.cargarRepuestos().pipe(
      delay(400),
      map((items) => {
        const repuesto = items.find((r) => r.codigo === codigo);
        if (!repuesto) {
          throw { status: 404, message: 'No existe un repuesto con ese código.' };
        }
        return { ...repuesto };
      }),
    );
  }

  buscarReparacion(id: number): Observable<ReparacionDto> {
    return this.http.get<{ items: ReparacionDto[] }>('mock/reparaciones.json').pipe(
      delay(400),
      map((pagina) => {
        const reparacion = pagina.items.find((r) => r.id === id);
        if (!reparacion) {
          throw { status: 404, message: 'No existe una reparación con ese número.' };
        }
        return reparacion;
      }),
    );
  }

  registrarUso(
    reparacionId: number,
    datos: UsoRepuestoCreateDto,
  ): Observable<UsoRepuestoResponseDto> {
    return this.buscarReparacion(reparacionId).pipe(
      switchMap(() => this.cargarRepuestos()),
      map((items) => {
        const repuesto = items.find((r) => r.id === datos.repuesto_id);
        if (!repuesto) {
          throw { status: 404, message: 'No existe el repuesto.' };
        }
        // TODO: RN-01 habla de stock físico; se valida contra el disponible porque RN-05 no permite usar lo reservado.
        if (datos.cantidad > repuesto.stock_disponible_total) {
          throw { status: 409, message: 'No hay stock disponible suficiente.' };
        }
        repuesto.stock_fisico_total -= datos.cantidad;
        repuesto.stock_disponible_total -= datos.cantidad;
        return {
          id: Date.now(),
          reparacion_id: reparacionId,
          cantidad: datos.cantidad,
          usada_en: new Date().toISOString(),
          repuesto: { id: repuesto.id, codigo: repuesto.codigo, nombre: repuesto.nombre },
        };
      }),
    );
  }
}
