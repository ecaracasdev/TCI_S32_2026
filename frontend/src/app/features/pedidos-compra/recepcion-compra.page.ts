import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmInputImports } from '@shared/ui/input';
import { HlmLabelImports } from '@shared/ui/label';
import { DataTableComponent } from '@shared/ui/table';
import { ToastService } from '../../core/services/toast.service';
import { environment } from '../../../environments/environment';
import { PEDIDOS_COMPRA_CONFIG } from './pedidos-compra.config';
import { ItemPedidoCompraDto, PedidoCompraDto, UbicacionDto } from './pedidos-compra.models';
import { PedidosCompraService } from './pedidos-compra.service';

type Carga = 'cargando' | 'listo' | 'error';

interface LineaPendiente {
  item: ItemPedidoCompraDto;
  recibidoPrevio: number;
  pendiente: number;
}

@Component({
  selector: 'app-recepcion-compra-page',
  standalone: true,
  imports: [
    RouterLink,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
    DataTableComponent,
  ],
  templateUrl: './recepcion-compra.page.html',
})
export class RecepcionCompraPage {
  private readonly servicio = inject(PedidosCompraService);
  private readonly toast = inject(ToastService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly ruta = inject(ActivatedRoute);
  private readonly router = inject(Router);

  protected readonly config = PEDIDOS_COMPRA_CONFIG;
  protected readonly esDemo = environment.useMockData;
  protected readonly pedidoId = Number(this.ruta.snapshot.paramMap.get('id'));

  protected readonly carga = signal<Carga>('cargando');
  protected readonly enviando = signal(false);
  protected readonly pedido = signal<PedidoCompraDto | null>(null);
  protected readonly ubicaciones = signal<UbicacionDto[]>([]);

  protected readonly cantidades = signal<Record<number, number>>({});
  protected readonly ubicacionElegida = signal<Record<number, number | null>>({});
  protected readonly delegadoA = signal('');
  protected readonly notas = signal('');
  protected readonly errores = signal<string[]>([]);

  protected readonly lineasPendientes = computed<LineaPendiente[]>(() => {
    const orden = this.pedido();
    if (!orden) return [];

    const recibidoPorItem = new Map<number, number>();
    for (const recepcion of orden.recepciones ?? []) {
      for (const item of recepcion.items ?? []) {
        recibidoPorItem.set(
          item.item_pedido_compra_id,
          (recibidoPorItem.get(item.item_pedido_compra_id) ?? 0) + item.cantidad,
        );
      }
    }

    return (orden.items ?? [])
      .map((item) => {
        const recibidoPrevio = recibidoPorItem.get(item.id) ?? 0;
        return { item, recibidoPrevio, pendiente: item.cantidad_solicitada - recibidoPrevio };
      })
      .filter((linea) => linea.pendiente > 0);
  });

  constructor() {
    this.cargar();
  }

  protected cargar(): void {
    this.carga.set('cargando');
    forkJoin({
      pedido: this.servicio.obtenerPorId(this.pedidoId),
      ubicaciones: this.servicio.listarUbicaciones(),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ pedido, ubicaciones }) => {
          this.pedido.set(pedido);
          this.ubicaciones.set(ubicaciones);
          this.carga.set('listo');
        },
        error: () => this.carga.set('error'),
      });
  }

  protected cantidad(itemId: number): number {
    return this.cantidades()[itemId] ?? 0;
  }

  protected cambiarCantidad(itemId: number, valor: string): void {
    const numero = Number(valor);
    this.cantidades.update((actual) => ({
      ...actual,
      [itemId]: Number.isFinite(numero) ? numero : 0,
    }));
  }

  protected ubicacion(itemId: number): number | null {
    return this.ubicacionElegida()[itemId] ?? null;
  }

  protected cambiarUbicacion(itemId: number, valor: string): void {
    const id = valor ? Number(valor) : null;
    this.ubicacionElegida.update((actual) => ({ ...actual, [itemId]: id }));
  }

  protected cambiarDelegado(valor: string): void {
    this.delegadoA.set(valor);
  }

  protected cambiarNotas(valor: string): void {
    this.notas.set(valor);
  }

  protected enviar(): void {
    const lineas = this.lineasPendientes()
      .map((linea) => ({
        item_pedido_compra_id: linea.item.id,
        cantidad: this.cantidad(linea.item.id),
        ubicacion_id: this.ubicacion(linea.item.id),
        pendiente: linea.pendiente,
      }))
      .filter((linea) => linea.cantidad > 0);

    const errores: string[] = [];
    if (lineas.length === 0) {
      errores.push(this.config.recepcion.cantidadInvalida);
    }
    for (const linea of lineas) {
      if (linea.cantidad > linea.pendiente) {
        errores.push(this.config.recepcion.cantidadInvalida);
      }
      if (!linea.ubicacion_id) {
        errores.push(this.config.recepcion.faltaUbicacion);
      }
    }
    this.errores.set([...new Set(errores)]);
    if (this.errores().length > 0) return;

    this.enviando.set(true);
    this.servicio
      .registrarRecepcion(this.pedidoId, {
        delegada_a_usuario_id: this.delegadoA() ? Number(this.delegadoA()) : null,
        notas: this.notas() || null,
        items: lineas.map((linea) => ({
          item_pedido_compra_id: linea.item_pedido_compra_id,
          ubicacion_id: linea.ubicacion_id as number,
          cantidad: linea.cantidad,
        })),
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.enviando.set(false);
          this.toast.show({ message: 'Recepción registrada.', variant: 'success' });
          this.router.navigate(['/pedidos-compra', this.pedidoId]);
        },
        error: () => {
          this.enviando.set(false);
          this.toast.show({ message: this.config.recepcion.errorEnviar, variant: 'error' });
        },
      });
  }
}
