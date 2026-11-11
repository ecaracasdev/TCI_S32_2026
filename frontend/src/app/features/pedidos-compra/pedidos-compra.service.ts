import { Observable } from 'rxjs';
import { PedidoCompraDto } from './pedidos-compra.models';

export abstract class PedidosCompraService {
  abstract listar(): Observable<PedidoCompraDto[]>;
  abstract obtenerPorId(id: number): Observable<PedidoCompraDto>;
}
