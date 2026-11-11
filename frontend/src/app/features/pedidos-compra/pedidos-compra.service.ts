import { Observable } from 'rxjs';
import {
  PedidoCompraDto,
  RecepcionCompraCreateDto,
  RecepcionCompraDto,
  UbicacionDto,
} from './pedidos-compra.models';

export abstract class PedidosCompraService {
  abstract listar(): Observable<PedidoCompraDto[]>;
  abstract obtenerPorId(id: number): Observable<PedidoCompraDto>;
  abstract listarUbicaciones(): Observable<UbicacionDto[]>;
  abstract registrarRecepcion(
    pedidoId: number,
    datos: RecepcionCompraCreateDto,
  ): Observable<RecepcionCompraDto>;
}
