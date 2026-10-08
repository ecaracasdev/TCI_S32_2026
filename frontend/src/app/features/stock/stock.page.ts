import { Component, computed, signal } from '@angular/core';

const STOCK_CONFIG = {
  title: 'Inventario de repuestos',
  description: 'Consultá existencias, disponibilidad y ubicación de cada repuesto en el almacén.',
  items: [
    { code: 'REP-00142', name: 'Rodamiento 6205-2RS', description: 'Rodamiento rígido de bolas · sellado', machines: 'Fraccionador F-02, Banda B-04', physical: 2, reserved: 0, minimum: 5, location: 'A-03-12', state: 'Bajo mínimo', tone: 'danger' },
    { code: 'REP-00087', name: 'Filtro de aceite FO-18', description: 'Filtro hidráulico de retorno', machines: 'Caldera C-01, Caldera C-02', physical: 4, reserved: 0, minimum: 6, location: 'B-01-04', state: 'Bajo mínimo', tone: 'warning' },
    { code: 'REP-00203', name: 'Correa dentada HTD-8M', description: 'Paso 8 mm · ancho 20 mm', machines: 'Banda transportadora B-04', physical: 1, reserved: 0, minimum: 3, location: 'A-02-08', state: 'Bajo mínimo', tone: 'danger' },
    { code: 'REP-00031', name: 'Junta tórica NBR 40 mm', description: 'Caucho nitrilo · alta presión', machines: 'Fraccionador F-01, F-02', physical: 18, reserved: 4, minimum: 8, location: 'C-02-11', state: 'Disponible', tone: 'good' },
    { code: 'REP-00106', name: 'Sensor de temperatura PT100', description: 'Sonda industrial · acero inoxidable', machines: 'Caldera C-01', physical: 7, reserved: 2, minimum: 3, location: 'B-04-02', state: 'Disponible', tone: 'good' },
    { code: 'REP-00056', name: 'Válvula de presión 1/2”', description: 'Acero inoxidable · 10 bar', machines: 'Caldera C-01, C-02', physical: 3, reserved: 1, minimum: 2, location: 'D-01-06', state: 'Disponible', tone: 'good' },
  ],
};

@Component({
  selector: 'app-stock-page',
  standalone: true,
  templateUrl: './stock.page.html',
  styleUrl: './stock.page.css',
})
export class StockPage {
  protected readonly config = STOCK_CONFIG;
  protected readonly query = signal('');
  protected readonly lowOnly = signal(false);
  protected readonly filteredItems = computed(() => {
    const term = this.query().trim().toLocaleLowerCase('es');
    return this.config.items.filter((item) => {
      const matchesText = !term || `${item.code} ${item.name} ${item.description} ${item.machines} ${item.location}`.toLocaleLowerCase('es').includes(term);
      const available = item.physical - item.reserved;
      return matchesText && (!this.lowOnly() || available <= item.minimum);
    });
  });

  protected updateQuery(event: Event): void {
    this.query.set((event.target as HTMLInputElement).value);
  }

  protected toggleLowOnly(): void {
    this.lowOnly.update((value) => !value);
  }
}
