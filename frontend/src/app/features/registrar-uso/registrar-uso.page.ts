import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmInputImports } from '@shared/ui/input';
import { HlmLabelImports } from '@shared/ui/label';
import { ToastService } from '../../core/services/toast.service';
import { environment } from '../../../environments/environment';
import { REGISTRAR_USO_CONFIG } from './registrar-uso.config';
import { RepuestoDto, UsoRepuestoCreateDto } from './registrar-uso.models';
import { RegistrarUsoService } from './registrar-uso.service';

@Component({
  selector: 'app-registrar-uso-page',
  standalone: true,
  imports: [ReactiveFormsModule, HlmButtonImports, HlmCardImports, HlmInputImports, HlmLabelImports],
  templateUrl: './registrar-uso.page.html',
})
export class RegistrarUsoPage {
  private readonly servicio = inject(RegistrarUsoService);
  private readonly toast = inject(ToastService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly fb = inject(FormBuilder);
  protected readonly config = REGISTRAR_USO_CONFIG;
  protected readonly esDemo = environment.useMockData;
  protected readonly repuesto = signal<RepuestoDto | null>(null);
  protected readonly buscando = signal(false);
  protected readonly enviando = signal(false);

  protected readonly form = this.fb.nonNullable.group({
    codigo: ['', Validators.required],
    reparacion_id: [null as number | null, [Validators.required, Validators.min(1)]],
    cantidad: [1, [Validators.required, Validators.min(1), Validators.pattern(/^[1-9]\d*$/)]],
  });

  protected escanear(): void {
    const codigos = this.config.repuesto.codigosDemo;
    const codigo = codigos[Math.floor(Math.random() * codigos.length)];
    this.form.controls.codigo.setValue(codigo);
    this.repuesto.set(null);
  }

  protected codigoCambiado(): void {
    this.repuesto.set(null);
  }

  protected buscarRepuesto(): void {
    const control = this.form.controls.codigo;
    const codigo = control.value.trim();
    control.setValue(codigo);
    if (!codigo) {
      control.markAsTouched();
      this.repuesto.set(null);
      return;
    }

    this.buscando.set(true);
    this.repuesto.set(null);
    this.servicio
      .buscarRepuesto(codigo)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (repuesto) => {
          this.repuesto.set(repuesto);
          this.buscando.set(false);
        },
        error: (error: { status?: number; message?: string }) => {
          this.buscando.set(false);
          this.repuesto.set(null);
          this.toast.show({
            variant: 'error',
            title: this.config.repuesto.noEncontrado,
            message:
              error.status === 404
                ? this.config.repuesto.noEncontrado
                : (error.message ?? this.config.errorGenerico),
          });
        },
      });
  }

  protected enviar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const repuesto = this.repuesto();
    if (!repuesto) {
      this.buscarRepuesto();
      return;
    }
    const reparacionId = this.form.controls.reparacion_id.value;
    if (reparacionId === null) {
      this.form.controls.reparacion_id.markAsTouched();
      return;
    }

    this.enviando.set(true);
    const cantidad = this.form.controls.cantidad.value;
    const datos: UsoRepuestoCreateDto = {
      repuesto_id: repuesto.id,
      cantidad,
    };
    this.servicio
      .registrarUso(reparacionId, datos)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.enviando.set(false);
          const stockDisponible = repuesto.stock_disponible_total - cantidad;
          this.repuesto.set({
            ...repuesto,
            stock_fisico_total: repuesto.stock_fisico_total - cantidad,
            stock_disponible_total: stockDisponible,
          });
          this.toast.show({
            variant: 'success',
            title: this.config.exito,
            message: this.esDemo ? this.config.demo : this.config.exito,
          });
          if (stockDisponible <= repuesto.stock_minimo) {
            this.toast.show({
              variant: 'warning',
              title: this.config.alertaTitulo,
              message: this.config.alertaUmbral,
            });
          }
          this.form.controls.cantidad.setValue(1);
        },
        error: (error: { status?: number; message?: string }) => {
          this.enviando.set(false);
          const message =
            error.status === 404
              ? this.config.reparacion.noEncontrada
              : error.status === 409
                ? this.config.stockInsuficiente
                : (error.message ?? this.config.errorGenerico);
          this.toast.show({
            variant: 'error',
            title: this.config.errorGenerico,
            message,
          });
        },
      });
  }
}
