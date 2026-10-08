import { Component, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

const PURCHASES_CONFIG = {
  title: 'Lista de compras',
  description: 'Revisá los repuestos que llegaron al umbral mínimo y prepará su reposición.',
  items: [
    { name: 'Rodamiento 6205-2RS', code: 'REP-00142', available: 2, minimum: 5, suggested: 8, urgency: 'Urgente', tone: 'danger', reason: 'Bajo mínimo', machine: 'Fraccionador F-02' },
    { name: 'Filtro de aceite FO-18', code: 'REP-00087', available: 4, minimum: 6, suggested: 6, urgency: 'Normal', tone: 'warning', reason: 'Bajo mínimo', machine: 'Caldera C-01' },
    { name: 'Correa dentada HTD-8M', code: 'REP-00203', available: 1, minimum: 3, suggested: 5, urgency: 'Urgente', tone: 'danger', reason: 'Requerimiento puntual', machine: 'Banda B-04' },
    { name: 'Junta tórica NBR 40 mm', code: 'REP-00031', available: 14, minimum: 8, suggested: 4, urgency: 'Normal', tone: 'info', reason: 'Previsión preventiva', machine: 'Fraccionador F-01' },
  ],
};

@Component({
  selector: 'app-purchases-page',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './purchases.page.html',
  styleUrl: './purchases.page.css',
})
export class PurchasesPage {
  protected readonly config = PURCHASES_CONFIG;
  protected readonly created = signal(false);
  protected readonly orderSent = signal(false);

  protected createOrder(): void {
    this.created.set(true);
  }

  protected sendOrder(): void {
    this.orderSent.set(true);
  }
}
