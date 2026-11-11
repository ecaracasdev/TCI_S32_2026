import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Pagina, PedidoCompraDto } from './pedidos-compra.models';
import { PedidosCompraService } from './pedidos-compra.service';

@Injectable({ providedIn: 'root' })
export class PedidosCompraHttpService extends PedidosCompraService {
    private readonly http = inject(HttpClient);
    private readonly url = `${environment.apiUrl}/api/v0/pedidos-compra`;

    listar(): Observable<PedidoCompraDto[]> {
        return this.http.get<Pagina<PedidoCompraDto>>(this.url).pipe(map((pagina) => pagina.items));
    }

    obtenerPorId(id: number): Observable<PedidoCompraDto> {
        return this.http.get<PedidoCompraDto>(`${this.url}/${id}`);
    }
}
