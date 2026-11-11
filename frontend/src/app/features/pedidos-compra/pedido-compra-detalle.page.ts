import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import {
    ESTADOS_PEDIDO,
    ORIGENES_COMPRA,
    PEDIDOS_COMPRA_CONFIG,
    URGENCIAS_COMPRA,
} from './pedidos-compra.config';
import { PedidoCompraDto } from './pedidos-compra.models';
import { PedidosCompraService } from './pedidos-compra.service';

type Carga = 'cargando' | 'listo' | 'error';

@Component({
    selector: 'app-pedido-compra-detalle-page',
    standalone: true,
    imports: [RouterLink, HlmBadgeImports, HlmButtonImports, HlmCardImports],
    templateUrl: './pedido-compra-detalle.page.html',
})
export class PedidoCompraDetallePage {
    private readonly servicio = inject(PedidosCompraService);
    private readonly destroyRef = inject(DestroyRef);
    private readonly ruta = inject(ActivatedRoute);

    protected readonly config = PEDIDOS_COMPRA_CONFIG;
    protected readonly pedido = signal<PedidoCompraDto | null>(null);
    protected readonly carga = signal<Carga>('cargando');

    constructor() {
        this.cargar();
    }

    protected cargar(): void {
        const id = Number(this.ruta.snapshot.paramMap.get('id'));
        this.carga.set('cargando');
        this.servicio
            .obtenerPorId(id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (pedido) => {
                    this.pedido.set(pedido);
                    this.carga.set('listo');
                },
                error: () => this.carga.set('error'),
            });
    }

    protected estado(valor: PedidoCompraDto['estado']) {
        return ESTADOS_PEDIDO[valor];
    }

    protected urgencia(valor: PedidoCompraDto['urgencia']) {
        return URGENCIAS_COMPRA[valor];
    }

    protected origen(valor: PedidoCompraDto['origen']): string {
        return ORIGENES_COMPRA[valor];
    }

    protected fecha(valor: string): string {
        return new Date(valor).toLocaleString('es-AR');
    }
}
