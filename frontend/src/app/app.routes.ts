import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '',            title: 'Resumen · Nexo Planta',      loadComponent: () => import('./features/dashboard/dashboard.page').then((page) => page.DashboardPage) },
  { path: 'stock',       title: 'Repuestos · Nexo Planta',    loadComponent: () => import('./features/stock/stock.page').then((page) =>             page.StockPage) },
  { path: 'incidencias', title: 'Incidencias · Nexo Planta',  loadComponent: () => import('./features/incidents/incidents.page').then((page) => page.IncidentsPage) },
  { path: 'compras',     title: 'Compras · Nexo Planta',      loadComponent: () => import('./features/purchases/purchases.page').then((page) => page.PurchasesPage) },
  { path: 'maquinas',    title: 'Máquinas · Nexo Planta',     loadComponent: () => import('./features/machines/machines.page').then((page) =>    page.MachinesPage) },
  { path: '**', redirectTo: '' },
];
