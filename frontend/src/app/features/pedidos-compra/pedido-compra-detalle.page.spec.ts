import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, provideRouter } from '@angular/router';
import { signal } from '@angular/core';
import { Observable, of, throwError } from 'rxjs';
import { SessionService } from '../../core/auth/session.service';
import { PedidoCompraDetallePage } from './pedido-compra-detalle.page';
import { EstadoPedido, PedidoCompraDto } from './pedidos-compra.models';
import { PedidosCompraService } from './pedidos-compra.service';

function pedido(estado: EstadoPedido, extra: Partial<PedidoCompraDto> = {}): PedidoCompraDto {
  return {
    id: 103,
    creada_por_usuario_id: 4,
    urgencia: 'normal',
    origen: 'manual',
    estado,
    creado_en: '2026-10-30T10:20:00Z',
    items: [],
    recepciones: [],
    ...extra,
  };
}

class ServicioFalso extends PedidosCompraService {
  aprobarLlamadas: number[] = [];
  cancelarLlamadas: { id: number; motivo: string }[] = [];
  falla = false;

  constructor(private readonly actual: PedidoCompraDto) {
    super();
  }

  listar() {
    return of([this.actual]);
  }
  obtenerPorId() {
    return of(this.actual);
  }
  listarUbicaciones() {
    return of([]);
  }
  registrarRecepcion(): Observable<never> {
    throw new Error('no se usa');
  }
  aprobar(id: number) {
    this.aprobarLlamadas.push(id);
    return this.falla
      ? throwError(() => new Error('500'))
      : of(
          pedido('confirmado', {
            revision_resuelta_por_usuario_id: 8,
            revision_resuelta_en: '2026-11-16T12:00:00Z',
          }),
        );
  }
  cancelar(id: number, datos: { motivo: string }) {
    this.cancelarLlamadas.push({ id, motivo: datos.motivo });
    return of(
      pedido('cancelado', {
        motivo_cancelacion: datos.motivo,
        revision_resuelta_por_usuario_id: 8,
        revision_resuelta_en: '2026-11-16T12:00:00Z',
      }),
    );
  }
}

async function montar(servicio: ServicioFalso, roles = ['encargado_mantenimiento']) {
  TestBed.configureTestingModule({
    providers: [
      provideRouter([]),
      { provide: PedidosCompraService, useValue: servicio },
      { provide: SessionService, useValue: { roles: signal(roles) } },
      { provide: ActivatedRoute, useValue: { snapshot: { paramMap: { get: () => '103' } } } },
    ],
  });
  const fixture = TestBed.createComponent(PedidoCompraDetallePage);
  await fixture.whenStable();
  fixture.detectChanges();
  const el = fixture.nativeElement as HTMLElement;
  const boton = (texto: string) =>
    Array.from(el.querySelectorAll('button')).find((b) => b.textContent?.includes(texto));
  return { fixture, el, boton };
}

describe('PedidoCompraDetallePage · resolver pedido', () => {
  it('a gerencia no le muestra aprobar, cancelar ni registrar recepción', async () => {
    const pendiente = await montar(new ServicioFalso(pedido('pendiente_aprobacion')), [
      'gerencia_administracion',
    ]);
    expect(pendiente.boton('Aprobar pedido')).toBeFalsy();
    expect(pendiente.boton('Cancelar pedido')).toBeFalsy();
    TestBed.resetTestingModule();

    const confirmado = await montar(new ServicioFalso(pedido('confirmado')), [
      'gerencia_administracion',
    ]);
    expect(confirmado.el.textContent).not.toContain('Registrar recepción');
  });

  it('muestra aprobar y cancelar solo en pendiente_aprobacion', async () => {
    const pendiente = await montar(new ServicioFalso(pedido('pendiente_aprobacion')));
    expect(pendiente.boton('Aprobar pedido')).toBeTruthy();
    expect(pendiente.boton('Cancelar pedido')).toBeTruthy();
    TestBed.resetTestingModule();

    for (const estado of [
      'creado',
      'pendiente_revision',
      'confirmado',
      'cancelado',
      'recibido',
    ] as const) {
      const otro = await montar(new ServicioFalso(pedido(estado)));
      expect(otro.boton('Aprobar pedido'), estado).toBeUndefined();
      expect(otro.boton('Cancelar pedido'), estado).toBeUndefined();
      TestBed.resetTestingModule();
    }
  });

  it('no aprueba hasta confirmar y luego muestra el nuevo estado y la resolución', async () => {
    const servicio = new ServicioFalso(pedido('pendiente_aprobacion'));
    const { fixture, el, boton } = await montar(servicio);

    boton('Aprobar pedido')!.click();
    fixture.detectChanges();
    expect(servicio.aprobarLlamadas).toEqual([]);

    boton('Sí, aprobar')!.click();
    fixture.detectChanges();
    expect(servicio.aprobarLlamadas).toEqual([103]);
    expect(el.textContent).toContain('Confirmado');
    expect(el.textContent).toContain('Resuelta por');
    expect(el.textContent).toContain('Usuario #8');
    expect(boton('Aprobar pedido')).toBeUndefined();
  });

  it('exige el motivo para cancelar y no llama al servicio sin él', async () => {
    const servicio = new ServicioFalso(pedido('pendiente_aprobacion'));
    const { fixture, el, boton } = await montar(servicio);

    boton('Cancelar pedido')!.click();
    fixture.detectChanges();
    boton('Confirmar cancelación')!.click();
    fixture.detectChanges();
    expect(servicio.cancelarLlamadas).toEqual([]);
    expect(el.textContent).toContain('El motivo de la cancelación es obligatorio.');

    const campo = el.querySelector('textarea')!;
    campo.value = '   ';
    campo.dispatchEvent(new Event('input'));
    boton('Confirmar cancelación')!.click();
    fixture.detectChanges();
    expect(servicio.cancelarLlamadas).toEqual([]);

    campo.value = 'Proveedor sin stock';
    campo.dispatchEvent(new Event('input'));
    boton('Confirmar cancelación')!.click();
    fixture.detectChanges();
    expect(servicio.cancelarLlamadas).toEqual([{ id: 103, motivo: 'Proveedor sin stock' }]);
    expect(el.textContent).toContain('Cancelado');
    expect(el.textContent).toContain('Proveedor sin stock');
  });

  it('muestra el error del servicio y mantiene el pedido pendiente', async () => {
    const servicio = new ServicioFalso(pedido('pendiente_aprobacion'));
    servicio.falla = true;
    const { fixture, el, boton } = await montar(servicio);

    boton('Aprobar pedido')!.click();
    fixture.detectChanges();
    boton('Sí, aprobar')!.click();
    fixture.detectChanges();

    expect(el.querySelector('[role="alert"]')?.textContent).toContain(
      'No se pudo resolver el pedido',
    );
    expect(el.textContent).toContain('Pendiente de aprobación');
    expect(boton('Sí, aprobar')).toBeTruthy();
  });
});
