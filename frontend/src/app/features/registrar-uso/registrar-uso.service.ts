import { Observable } from 'rxjs';
import {
  ReparacionDto,
  RepuestoDto,
  UsoRepuestoCreateDto,
  UsoRepuestoResponseDto,
} from './registrar-uso.models';

export abstract class RegistrarUsoService {
  abstract buscarRepuesto(codigo: string): Observable<RepuestoDto>;
  abstract buscarReparacion(id: number): Observable<ReparacionDto>;
  abstract registrarUso(
    reparacionId: number,
    datos: UsoRepuestoCreateDto,
  ): Observable<UsoRepuestoResponseDto>;
}
