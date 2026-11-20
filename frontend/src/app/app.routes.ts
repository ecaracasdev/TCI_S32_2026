import { inject } from '@angular/core';
import { Routes } from '@angular/router';
import { environment } from '../environments/environment';
import { authGuard } from './core/auth/auth.guard';
import {
  ROLES_CONSULTA_INCIDENCIAS,
  ROLES_CONSULTA_PEDIDOS,
  ROLES_GESTION_PEDIDOS,
  ROLES_LECTURA_PLANTA,
  ROLES_REPARACION,
  ROLES_REPORTE_INCIDENCIA,
  rolGuard,
} from './core/auth/roles.guard';
import { MockRegistrarUsoService } from './features/registrar-uso/mock-registrar-uso.service';
import { RegistrarUsoHttpService } from './features/registrar-uso/registrar-uso.http.service';
import { RegistrarUsoService } from './features/registrar-uso/registrar-uso.service';
import { ConsultaIncidenciasHttpService } from './features/consulta-incidencias/consulta-incidencias.http.service';
import { ConsultaIncidenciasService } from './features/consulta-incidencias/consulta-incidencias.service';
import { MockConsultaIncidenciasService } from './features/consulta-incidencias/mock-consulta-incidencias.service';
import { MockReportarIncidenciaService } from './features/reportar-incidencia/mock-reportar-incidencia.service';
import { ReportarIncidenciaHttpService } from './features/reportar-incidencia/reportar-incidencia.http.service';
import { ReportarIncidenciaService } from './features/reportar-incidencia/reportar-incidencia.service';
import { ROLES_ESCRITURA } from './features/repuestos/repuestos.models';
import { InicioHttpService } from './features/inicio/inicio.http.service';
import { InicioService } from './features/inicio/inicio.service';
import { MockInicioService } from './features/inicio/mock-inicio.service';
import { MockRepuestosService } from './features/repuestos/mock-repuestos.service';
import { RepuestosHttpService } from './features/repuestos/repuestos.http.service';
import { RepuestosService } from './features/repuestos/repuestos.service';
import { MockPedidosCompraService } from './features/pedidos-compra/mock-pedidos-compra.service';
import { PedidosCompraHttpService } from './features/pedidos-compra/pedidos-compra.http.service';
import { PedidosCompraService } from './features/pedidos-compra/pedidos-compra.service';
import { MaquinasHttpService } from './features/maquinas/maquinas.http.service';
import { MockMaquinasService } from './features/maquinas/mock-maquinas.service';
import { MaquinasService } from './features/maquinas/maquinas.service';

export const routes: Routes = [
  {
    path: 'login',
    title: 'Iniciar sesión · TCI',
    loadComponent: () => import('./features/auth/login.page').then((page) => page.LoginPage),
  },

  {
    path: '',
    canActivate: [authGuard],
    children: [
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'inicio',
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
        loadComponent: () =>
          import('./features/inicio/inicio.page').then((page) => page.InicioPage),
      },

      {
        path: 'stock',
        canActivate: [rolGuard(ROLES_LECTURA_PLANTA)],
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
            loadComponent: () =>
              import('./features/repuestos/repuestos.page').then((page) => page.RepuestosPage),
          },
          {
            path: 'nuevo',
            canActivate: [rolGuard(ROLES_ESCRITURA)],
            title: 'Nuevo repuesto · TCI',
            loadComponent: () =>
              import('./features/repuestos/repuesto-form.page').then(
                (page) => page.RepuestoFormPage,
              ),
          },
          {
            path: ':id/editar',
            canActivate: [rolGuard(ROLES_ESCRITURA)],
            title: 'Editar repuesto · TCI',
            loadComponent: () =>
              import('./features/repuestos/repuesto-form.page').then(
                (page) => page.RepuestoFormPage,
              ),
          },
          {
            path: ':id',
            title: 'Detalle de repuesto · TCI',
            loadComponent: () =>
              import('./features/repuestos/repuesto-detalle.page').then(
                (page) => page.RepuestoDetallePage,
              ),
          },
        ],
      },

      {
        path: 'ubicaciones',
        canActivate: [rolGuard(ROLES_LECTURA_PLANTA)],
        title: 'Ubicaciones · TCI',
        providers: [
          {
            provide: RepuestosService,
            useFactory: () =>
              environment.useMockData ? inject(MockRepuestosService) : inject(RepuestosHttpService),
          },
        ],
        loadComponent: () =>
          import('./features/repuestos/ubicaciones.page').then((page) => page.UbicacionesPage),
      },

      {
        path: 'reposicion',
        canActivate: [rolGuard(ROLES_LECTURA_PLANTA)],
        providers: [
          {
            provide: RepuestosService,
            useFactory: () =>
              environment.useMockData ? inject(MockRepuestosService) : inject(RepuestosHttpService),
          },
        ],
        loadComponent: () =>
          import('./features/reposicion-repuestos/reposicion-repuestos.page').then(
            (page) => page.ReposicionRepuestosPage,
          ),
      },

      {
        path: 'compras',
        canActivate: [rolGuard(ROLES_LECTURA_PLANTA)],
        providers: [
          {
            provide: RepuestosService,
            useFactory: () =>
              environment.useMockData ? inject(MockRepuestosService) : inject(RepuestosHttpService),
          },
        ],
        loadComponent: () =>
          import('./features/compras/compras.page').then((page) => page.ComprasPage),
      },

      {
        path: 'pedidos-compra',
        canActivate: [rolGuard(ROLES_CONSULTA_PEDIDOS)],
        providers: [
          {
            provide: PedidosCompraService,
            useFactory: () =>
              environment.useMockData
                ? inject(MockPedidosCompraService)
                : inject(PedidosCompraHttpService),
          },
        ],
        children: [
          {
            path: '',
            title: 'Pedidos de compra · TCI',
            loadComponent: () =>
              import('./features/pedidos-compra/pedidos-compra.page').then(
                (page) => page.PedidosCompraPage,
              ),
          },
          {
            path: ':id',
            title: 'Detalle de pedido · TCI',
            loadComponent: () =>
              import('./features/pedidos-compra/pedido-compra-detalle.page').then(
                (page) => page.PedidoCompraDetallePage,
              ),
          },
          {
            path: ':id/recepcion',
            canActivate: [rolGuard(ROLES_GESTION_PEDIDOS)],
            title: 'Registrar recepción · TCI',
            loadComponent: () =>
              import('./features/pedidos-compra/recepcion-compra.page').then(
                (page) => page.RecepcionCompraPage,
              ),
          },
        ],
      },

      // Va antes que 'incidencias': si no, 'nueva' se toma como el :id del detalle.
      {
        path: 'incidencias/nueva',
        title: 'Reportar incidencia · TCI',
        canActivate: [rolGuard(ROLES_REPORTE_INCIDENCIA)],
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
        path: 'incidencias',
        canActivate: [rolGuard(ROLES_CONSULTA_INCIDENCIAS)],
        providers: [
          {
            provide: ConsultaIncidenciasService,
            useFactory: () =>
              environment.useMockData
                ? inject(MockConsultaIncidenciasService)
                : inject(ConsultaIncidenciasHttpService),
          },
        ],
        children: [
          {
            path: '',
            title: 'Consulta de incidencias · TCI',
            loadComponent: () =>
              import('./features/consulta-incidencias/consulta-incidencias.page').then(
                (page) => page.ConsultaIncidenciasPage,
              ),
          },
          {
            path: ':id',
            title: 'Detalle de incidencia · TCI',
            loadComponent: () =>
              import('./features/consulta-incidencias/incidencia-detalle.page').then(
                (page) => page.IncidenciaDetallePage,
              ),
          },
        ],
      },

      {
        path: 'usos/nuevo',
        title: 'Registrar uso de repuesto · TCI',
        canActivate: [rolGuard(ROLES_REPARACION)],
        providers: [
          {
            provide: RegistrarUsoService,
            useFactory: () =>
              environment.useMockData
                ? inject(MockRegistrarUsoService)
                : inject(RegistrarUsoHttpService),
          },
        ],
        loadComponent: () =>
          import('./features/registrar-uso/registrar-uso.page').then(
            (page) => page.RegistrarUsoPage,
          ),
      },

      {
        path: 'maquinas',
        canActivate: [rolGuard(ROLES_LECTURA_PLANTA)],
        providers: [
          {
            provide: MaquinasService,
            useFactory: () =>
              environment.useMockData ? inject(MockMaquinasService) : inject(MaquinasHttpService),
          },
        ],
        children: [
          {
            path: '',
            title: 'Máquinas · TCI',
            loadComponent: () =>
              import('./features/maquinas/maquinas.page').then((page) => page.MaquinasPage),
          },
          {
            path: ':id',
            title: 'Detalle de máquina · TCI',
            loadComponent: () =>
              import('./features/maquinas/maquina-detalle.page').then(
                (page) => page.MaquinaDetallePage,
              ),
          },
        ],
      },
    ],
  },

  {
    path: '**',
    title: 'Pantalla en desarrollo · TCI',
    loadComponent: () =>
      import('./features/en-desarrollo/en-desarrollo.page').then((page) => page.EnDesarrolloPage),
  },
];
