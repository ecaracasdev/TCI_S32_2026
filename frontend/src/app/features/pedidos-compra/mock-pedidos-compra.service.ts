import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { Pagina, PedidoCompraDto } from './pedidos-compra.models';
import { PedidosCompraService } from './pedidos-compra.service';

@Injectable({ providedIn: 'root' })
export class MockPedidosCompraService extends PedidosCompraService {
    private readonly http = inject(HttpClient);
    private readonly fixture = 'mock/pedidos-compra.json';

    listar(): Observable<PedidoCompraDto[]> {
        return this.http
            .get<Pagina<PedidoCompraDto>>(this.fixture)
            .pipe(map((pagina) => pagina.items));
    }

    obtenerPorId(id: number): Observable<PedidoCompraDto> {
        return this.http.get<Pagina<PedidoCompraDto>>(this.fixture).pipe(
            map((pagina) => {
                const pedido = pagina.items.find((item) => item.id === id);
                if (!pedido) throw new Error(`No existe el pedido ${id}`);
                return pedido;
            }),
        );
    }
}
