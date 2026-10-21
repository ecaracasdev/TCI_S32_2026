import { inject } from '@angular/core';
import { Routes } from '@angular/router';
import { environment } from '../environments/environment';
import { InicioHttpService } from './features/inicio/inicio.http.service';
import { InicioService } from './features/inicio/inicio.service';
import { MockInicioService } from './features/inicio/mock-inicio.service';

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
    providers: [
      {
        provide: InicioService,
        useFactory: () =>
          environment.useMockData ? inject(MockInicioService) : inject(InicioHttpService),
      },
    ],
    loadComponent: () => import('./features/inicio/inicio.page').then((page) => page.InicioPage),
  },
  { path: '**', redirectTo: 'ui-preview' },
];
