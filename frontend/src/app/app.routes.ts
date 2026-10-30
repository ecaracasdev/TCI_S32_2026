import { inject } from '@angular/core';
import { Routes } from '@angular/router';
import { environment } from '../environments/environment';
import { InicioHttpService } from './features/inicio/inicio.http.service';
import { InicioService } from './features/inicio/inicio.service';
import { MockInicioService } from './features/inicio/mock-inicio.service';
import { MockRepuestosService } from './features/repuestos/mock-repuestos.service';
import { RepuestosHttpService } from './features/repuestos/repuestos.http.service';
import { RepuestosService } from './features/repuestos/repuestos.service';
import { ReportarIncidenciaHttpService } from './features/reportar-incidencia/reportar-incidencia.http.service';
import { ReportarIncidenciaService } from './features/reportar-incidencia/reportar-incidencia.service';
import { MockReportarIncidenciaService } from './features/reportar-incidencia/mock-reportar-incidencia.service';
import { RegistrarUsoHttpService } from './features/registrar-uso/registrar-uso.http.service';
import { RegistrarUsoService } from './features/registrar-uso/registrar-uso.service';
import { MockRegistrarUsoService } from './features/registrar-uso/mock-registrar-uso.service';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'ui-preview' },
  {
    path: 'ui-preview',
    title: 'Componentes visuales · TCI',
    loadComponent: () => import('./features/ui-preview/ui-preview.page').then((page) => page.UiPreviewPage),
  },
  {
    path: 'inicio',
    title: 'Inicio · TCI',
    // Mock o real según environment.useMockData
    providers: [
      {
        provide: InicioService,
        useFactory: () =>
          environment.useMockData ? inject(MockInicioService) : inject(InicioHttpService),
      },
    ],
    loadComponent: () => import('./features/inicio/inicio.page').then((page) => page.InicioPage),
  },
  {
    // T12: inventario de repuestos (listado y detalle). Mock o real según environment.useMockData
    path: 'stock',
    providers: [
      {
        provide: RepuestosService,
        useFactory: () =>
          environment.useMockData ? inject(MockRepuestosService) : inject(RepuestosHttpService),
      },
    ],
    children: [
      {
        path: '',
        title: 'Repuestos · TCI',
        loadComponent: () => import('./features/repuestos/repuestos.page').then((page) => page.RepuestosPage),
      },
      {
        path: ':id',
        title: 'Detalle de repuesto · TCI',
        loadComponent: () =>
          import('./features/repuestos/repuesto-detalle.page').then((page) => page.RepuestoDetallePage),
      },
    ],
  },
  {
    path: 'incidencias/nueva',
    title: 'Reportar incidencia · TCI',
    providers: [
      {
        provide: ReportarIncidenciaService,
        useFactory: () =>
          environment.useMockData
            ? inject(MockReportarIncidenciaService)
            : inject(ReportarIncidenciaHttpService),
      },
    ],
    loadComponent: () =>
      import('./features/reportar-incidencia/reportar-incidencia.page').then(
        (page) => page.ReportarIncidenciaPage,
      ),
  },
  {
    path: 'usos/nuevo',
    title: 'Registrar uso de repuesto · TCI',
    providers: [
      {
        provide: RegistrarUsoService,
        useFactory: () =>
          environment.useMockData ? inject(MockRegistrarUsoService) : inject(RegistrarUsoHttpService),
      },
    ],
    loadComponent: () =>
      import('./features/registrar-uso/registrar-uso.page').then((page) => page.RegistrarUsoPage),
  },
  // El comodín va siempre al final: cualquier ruta nueva debe agregarse antes.
  { path: '**', redirectTo: 'ui-preview' },
];