import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'ui-preview' },
  {
    path: 'ui-preview',
    title: 'Componentes visuales · TCI',
    loadComponent: () => import('./features/ui-preview/ui-preview.page').then((page) => page.UiPreviewPage),
  },
  { path: '**', redirectTo: 'ui-preview' },
];
