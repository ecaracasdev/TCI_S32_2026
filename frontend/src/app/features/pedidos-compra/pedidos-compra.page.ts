import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { DataTableComponent } from '@shared/ui/table';
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
  selector: 'app-pedidos-compra-page',
  standalone: true,
  imports: [RouterLink, HlmBadgeImports, HlmButtonImports, HlmCardImports, DataTableComponent],
  templateUrl: './pedidos-compra.page.html',
})
export class PedidosCompraPage {
  private readonly servicio = inject(PedidosCompraService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly config = PEDIDOS_COMPRA_CONFIG;
  protected readonly pedidos = signal<PedidoCompraDto[]>([]);
  protected readonly carga = signal<Carga>('cargando');

  constructor() {
    this.cargar();
  }

  protected cargar(): void {
    this.carga.set('cargando');
    this.servicio
      .listar()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (pedidos) => {
          this.pedidos.set(pedidos);
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
    return new Date(valor).toLocaleDateString('es-AR');
  }
}
