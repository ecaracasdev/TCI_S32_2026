import { Component, input, output } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { IconComponent } from '@shared/ui/icon';

export interface PurchaseDryRunLine {
  code: string;
  name: string;
  reason: string;
  quantity: number;
}

export interface PurchaseHistorySummary {
  code: string;
  items: number;
  date: string;
  status: string;
}

const ORDER_REVIEW_CONFIG = {
  eyebrow: 'SIMULACIÓN · DRY RUN',
  title: 'Revisión de orden de compra',
  description: 'Simulación: revisá las líneas y el historial antes de confirmar.',
  itemCount: 'Elementos',
  priority: 'Prioridad estimada',
  status: 'Estado',
  unregistered: 'Sin registrar',
  contents: 'Contenido de la orden',
  history: 'Historial de referencia',
  notice: 'Es una vista previa; confirmar no guarda ni envía una orden real.',
  cancel: 'No, volver',
  confirm: 'Sí, generar orden',
} as const;

@Component({
  selector: 'app-order-review-dialog',
  standalone: true,
  imports: [DecimalPipe, HlmBadgeImports, HlmButtonImports, IconComponent],
  template: `
    <div class="dialog-backdrop" (click)="cancel.emit()" (keydown.escape)="cancel.emit()">
      <section class="order-dialog" role="dialog" aria-modal="true" aria-labelledby="order-dialog-title" (click)="$event.stopPropagation()">
        <header class="dialog-heading">
          <div><p class="eyebrow">{{ config.eyebrow }}</p><h2 id="order-dialog-title">{{ config.title }}</h2><p>{{ config.description }}</p></div>
          <button class="dialog-close" type="button" aria-label="Cerrar" (click)="cancel.emit()">×</button>
        </header>
        <div class="dialog-summary">
          <span><small>{{ config.itemCount }}</small><strong class="numeric">{{ items().length | number:'2.0-0' }}</strong></span>
          <span><small>{{ config.priority }}</small><strong>{{ priority() }}</strong></span>
          <span><small>{{ config.status }}</small><strong>{{ config.unregistered }}</strong></span>
        </div>
        <div class="dialog-section">
          <h3>{{ config.contents }}</h3>
          <div class="dry-run-lines">
            @for (item of items(); track item.code) {
              <div class="dry-run-line"><div><strong>{{ item.name }}</strong><small>{{ item.code }} · {{ item.reason }}</small></div><span><small>Cantidad</small><b class="numeric">{{ item.quantity | number:'3.0-0' }}</b></span></div>
            }
          </div>
        </div>
        <div class="dialog-section">
          <h3>{{ config.history }}</h3>
          <div class="history-list">
            @for (order of history(); track order.code) {
              <div><strong>#{{ order.code }}</strong><span>{{ order.items }} repuestos · {{ order.date }}</span><span hlmBadge [variant]="order.status === 'Pendiente' ? 'secondary' : 'outline'">{{ order.status }}</span></div>
            }
          </div>
        </div>
        <p class="dry-run-notice"><app-icon name="alert" class="size-4" /> {{ config.notice }}</p>
        <footer class="dialog-actions">
          <button hlmBtn variant="outline" type="button" (click)="cancel.emit()">{{ config.cancel }}</button>
          <button hlmBtn type="button" (click)="confirm.emit()">{{ config.confirm }} <app-icon name="check" /></button>
        </footer>
      </section>
    </div>
  `,
  styles: `
    .dialog-backdrop { position: fixed; inset: 0; z-index: 80; display: grid; place-items: center; padding: .75rem; background: color-mix(in oklch, var(--ui-text) 45%, transparent); }
    .order-dialog { display: grid; width: min(100%, 42rem); max-height: min(92dvh, 54rem); gap: 1rem; overflow-y: auto; padding: 1rem; border: 1px solid var(--ui-border); border-radius: 1rem; background: var(--ui-surface); box-shadow: 0 1.5rem 4rem color-mix(in oklch, var(--ui-text) 25%, transparent); }
    .dialog-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: .75rem; padding-bottom: .85rem; border-bottom: 1px solid var(--ui-border); }
    .eyebrow { margin: 0; color: var(--ui-text-muted); font-size: .68rem; font-weight: 700; letter-spacing: .13em; }
    .dialog-heading h2 { margin: .3rem 0 0; font-size: 1.1rem; font-weight: 650; }
    .dialog-heading p:not(.eyebrow) { margin: .35rem 0 0; color: var(--ui-text-muted); font-size: .75rem; line-height: 1.45; }
    .dialog-close { display: grid; width: 2rem; height: 2rem; flex: none; place-items: center; border: 1px solid var(--ui-border); border-radius: .6rem; background: var(--ui-surface); color: var(--ui-text-muted); font-size: 1.25rem; cursor: pointer; }
    .dialog-summary { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .5rem; }
    .dialog-summary > span { display: grid; align-content: start; gap: .3rem; min-width: 0; padding: .65rem; border: 1px solid var(--ui-border); border-radius: .65rem; background: var(--ui-surface-muted); }
    .dialog-summary small { color: var(--ui-text-muted); font-size: .62rem; }
    .dialog-summary strong { overflow-wrap: anywhere; font-size: .75rem; font-weight: 650; text-transform: capitalize; }
    .dialog-section { display: grid; gap: .5rem; }
    .dialog-section h3 { margin: 0; font-size: .8rem; font-weight: 650; }
    .dry-run-lines, .history-list { display: grid; border-top: 1px solid var(--ui-border); }
    .dry-run-line, .history-list > div { display: flex; align-items: center; justify-content: space-between; gap: .7rem; padding: .65rem 0; border-bottom: 1px solid var(--ui-border); }
    .dry-run-line > div, .dry-run-line > span { display: grid; min-width: 0; gap: .16rem; }
    .dry-run-line strong, .history-list strong { overflow: hidden; font-size: .74rem; font-weight: 620; text-overflow: ellipsis; white-space: nowrap; }
    .dry-run-line small, .history-list > div > span:not([hlmBadge]) { color: var(--ui-text-muted); font-size: .65rem; }
    .dry-run-line > span { justify-items: end; flex: none; }
    .dry-run-line b { font-size: .8rem; }
    .history-list > div > span:last-child { flex: none; }
    .dry-run-notice { display: flex; align-items: flex-start; gap: .5rem; margin: 0; padding: .7rem; border: 1px solid var(--ui-border); border-radius: .65rem; background: var(--ui-surface-muted); color: var(--ui-text-muted); font-size: .68rem; line-height: 1.45; }
    .dry-run-notice app-icon { flex: none; }
    .dialog-actions { display: flex; flex-direction: column-reverse; gap: .55rem; padding-top: .2rem; }
    .dialog-actions button { justify-content: center; }
    .dialog-actions app-icon { width: 1rem; height: 1rem; }
    @media (min-width: 560px) { .dialog-actions { flex-direction: row; justify-content: flex-end; } .dialog-actions button { min-width: 9rem; } }
    @media (min-width: 800px) { .order-dialog { padding: 1.35rem; } }
  `,
})
export class OrderReviewDialogComponent {
  protected readonly config = ORDER_REVIEW_CONFIG;
  readonly items = input.required<readonly PurchaseDryRunLine[]>();
  readonly priority = input.required<string>();
  readonly history = input.required<readonly PurchaseHistorySummary[]>();
  readonly cancel = output<void>();
  readonly confirm = output<void>();
}
