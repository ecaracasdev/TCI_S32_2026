import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ROLES_GESTION_PEDIDOS, tieneAlgunRol } from '../../core/auth/roles.guard';
import { SessionService } from '../../core/auth/session.service';
import { ToastService } from '../../core/services/toast.service';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmInputImports } from '@shared/ui/input';
import { HlmLabelImports } from '@shared/ui/label';
import {
  ESTADOS_PEDIDO,
  ORIGENES_COMPRA,
  PEDIDOS_COMPRA_CONFIG,
  URGENCIAS_COMPRA,
} from './pedidos-compra.config';
import { PedidoCompraDto } from './pedidos-compra.models';
import { PedidosCompraService } from './pedidos-compra.service';

type Carga = 'cargando' | 'listo' | 'error';
type Panel = 'aprobar' | 'cancelar' | null;

@Component({
  selector: 'app-pedido-compra-detalle-page',
  standalone: true,
  imports: [
    RouterLink,
    HlmBadgeImports,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
  ],
  templateUrl: './pedido-compra-detalle.page.html',
})
export class PedidoCompraDetallePage {
  private readonly servicio = inject(PedidosCompraService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly ruta = inject(ActivatedRoute);
  private readonly toast = inject(ToastService);
  private readonly sesion = inject(SessionService);

  protected readonly config = PEDIDOS_COMPRA_CONFIG;
  protected readonly pedido = signal<PedidoCompraDto | null>(null);
  protected readonly carga = signal<Carga>('cargando');
  protected readonly esDemo = environment.useMockData;

  protected readonly panel = signal<Panel>(null);
  protected readonly motivo = signal('');
  protected readonly motivoInvalido = signal(false);
  protected readonly resolviendo = signal(false);
  protected readonly errorAccion = signal(false);

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

  protected abrirPanel(panel: Exclude<Panel, null>): void {
    this.panel.set(panel);
    this.errorAccion.set(false);
    this.motivoInvalido.set(false);
  }

  protected cerrarPanel(): void {
    this.panel.set(null);
    this.motivo.set('');
    this.motivoInvalido.set(false);
    this.errorAccion.set(false);
  }

  protected cambiarMotivo(valor: string): void {
    this.motivo.set(valor);
    if (valor.trim()) this.motivoInvalido.set(false);
  }

  protected aprobar(): void {
    const pedido = this.pedido();
    if (!pedido || this.resolviendo()) return;
    this.resolver(this.servicio.aprobar(pedido.id), this.config.revision.exitoAprobar);
  }

  protected cancelar(): void {
    const pedido = this.pedido();
    if (!pedido || this.resolviendo()) return;

    const motivo = this.motivo().trim();
    if (!motivo) {
      this.motivoInvalido.set(true);
      return;
    }
    this.resolver(
      this.servicio.cancelar(pedido.id, { motivo }),
      this.config.revision.exitoCancelar,
    );
  }

  private resolver(accion: Observable<PedidoCompraDto>, exito: string): void {
    this.resolviendo.set(true);
    this.errorAccion.set(false);
    accion.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (actualizado) => {
        this.pedido.set(actualizado);
        this.resolviendo.set(false);
        this.cerrarPanel();
        this.toast.show({ message: exito, variant: 'success' });
      },
      error: () => {
        this.resolviendo.set(false);
        this.errorAccion.set(true);
        this.toast.show({ message: this.config.revision.error, variant: 'error' });
      },
    });
  }

  protected puedeResolver(pedido: PedidoCompraDto): boolean {
    return this.puedeGestionar() && pedido.estado === 'pendiente_aprobacion';
  }

  private puedeGestionar(): boolean {
    return tieneAlgunRol(this.sesion.roles(), ROLES_GESTION_PEDIDOS);
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

  protected puedeRegistrarRecepcion(pedido: PedidoCompraDto): boolean {
    return (
      this.puedeGestionar() &&
      (pedido.estado === 'confirmado' || pedido.estado === 'pendiente_recepcion')
    );
  }
}
