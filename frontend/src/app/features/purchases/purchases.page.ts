import { Component, computed, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmBadgeImports } from '@shared/ui/badge';
import { IconComponent } from '@shared/ui/icon';
import { DataTableComponent } from '@shared/ui/table';

type StockFilter = 'out' | 'low' | 'normal';

const PURCHASES_CONFIG = {
  title: 'Lista de compras',
  description: 'Revisá los repuestos que llegaron al umbral mínimo y prepará su reposición.',
  preparedMessage: 'Pedido de muestra preparado. Revisá las cantidades antes de continuar.',
  sentMessage: 'Vista previa: se mostraría el aviso para las personas responsables.',
  filters: [
    { value: 'out', label: 'Sin stock' },
    { value: 'low', label: 'Bajo mínimo' },
    { value: 'normal', label: 'Stock normal' },
  ] as const,
  items: [
    { name: 'Rodamiento 6205-2RS', code: 'REP-00142', available: 2, minimum: 5, suggested: 8, urgency: 'Bajo mínimo', tone: 'warning', stockGroup: 'low', reason: 'Bajo mínimo', machine: 'Fraccionador F-02' },
    { name: 'Filtro de aceite FO-18', code: 'REP-00087', available: 4, minimum: 6, suggested: 6, urgency: 'Bajo mínimo', tone: 'warning', stockGroup: 'low', reason: 'Bajo mínimo', machine: 'Caldera C-01' },
    { name: 'Correa dentada HTD-8M', code: 'REP-00203', available: 0, minimum: 3, suggested: 5, urgency: 'Urgente', tone: 'danger', stockGroup: 'out', reason: 'Sin stock', machine: 'Banda B-04' },
    { name: 'Junta tórica NBR 40 mm', code: 'REP-00031', available: 14, minimum: 8, suggested: 4, urgency: 'Normal', tone: 'good', stockGroup: 'normal', reason: 'Previsión preventiva', machine: 'Fraccionador F-01' },
  ],
};

@Component({
  selector: 'app-purchases-page',
  standalone: true,
  imports: [RouterLink, DecimalPipe, HlmButtonImports, HlmCardImports, HlmBadgeImports, IconComponent, DataTableComponent],
  templateUrl: './purchases.page.html',
  styleUrl: './purchases.page.css',
})
export class PurchasesPage {
  protected readonly config = PURCHASES_CONFIG;
  protected readonly created = signal(false);
  protected readonly orderSent = signal(false);
  protected readonly activeFilter = signal<StockFilter>('out');
  protected readonly selectedCodes = signal(new Set(PURCHASES_CONFIG.items.slice(0, 3).map((item) => item.code)));
  protected readonly visibleItems = computed(() => PURCHASES_CONFIG.items.filter((item) => item.stockGroup === this.activeFilter()));
  protected readonly selectedCount = computed(() => this.selectedCodes().size);
  protected readonly selectedVisibleCount = computed(() => this.visibleItems().filter((item) => this.selectedCodes().has(item.code)).length);
  protected readonly allVisibleSelected = computed(() => this.visibleItems().length > 0 && this.visibleItems().every((item) => this.selectedCodes().has(item.code)));
  protected readonly orderPriority = computed(() => {
    const selected = this.selectedCodes();
    if (selected.size === 0) return 'sin prioridad';
    if (PURCHASES_CONFIG.items.some((item) => selected.has(item.code) && item.stockGroup === 'out')) return 'urgente';
    if (PURCHASES_CONFIG.items.some((item) => selected.has(item.code) && item.stockGroup === 'low')) return 'bajo mínimo';
    return 'normal';
  });
  protected readonly quantities = signal<Record<string, number>>(Object.fromEntries(
    PURCHASES_CONFIG.items.map((item) => [item.code, item.suggested]),
  ));

  protected isSelected(code: string): boolean {
    return this.selectedCodes().has(code);
  }

  protected countFor(filter: StockFilter): number {
    return PURCHASES_CONFIG.items.filter((item) => item.stockGroup === filter).length;
  }

  protected setFilter(filter: StockFilter): void {
    this.activeFilter.set(filter);
  }

  protected toggleItem(code: string, event: Event): void {
    const selected = new Set(this.selectedCodes());
    if ((event.target as HTMLInputElement).checked) selected.add(code);
    else selected.delete(code);
    this.selectedCodes.set(selected);
  }

  protected toggleAll(event: Event): void {
    const selected = new Set(this.selectedCodes());
    for (const item of this.visibleItems()) {
      if ((event.target as HTMLInputElement).checked) selected.add(item.code);
      else selected.delete(item.code);
    }
    this.selectedCodes.set(selected);
  }

  protected quantityFor(code: string): number {
    return this.quantities()[code] ?? 1;
  }

  protected adjustQuantity(code: string, difference: number): void {
    this.quantities.update((quantities) => ({
      ...quantities,
      [code]: Math.max(1, (quantities[code] ?? 1) + difference),
    }));
  }

  protected createOrder(): void {
    this.created.set(true);
  }

  protected sendOrder(): void {
    this.orderSent.set(true);
  }
}
