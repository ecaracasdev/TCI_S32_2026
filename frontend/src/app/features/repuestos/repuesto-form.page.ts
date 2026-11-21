import { HttpErrorResponse } from '@angular/common/http';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmInputImports } from '@shared/ui/input';
import { HlmLabelImports } from '@shared/ui/label';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ToastService } from '../../core/services/toast.service';
import { EscanerCodigoComponent } from './escaner-codigo.component';
import { REPUESTOS_CONFIG } from './repuestos.config';
import { RepuestoDto } from './repuestos.models';
import { RepuestosService } from './repuestos.service';

type Carga = 'cargando' | 'listo' | 'error';

/** Alta (`/stock/nuevo`) y edición (`/stock/:id/editar`) de un repuesto del catálogo. */
@Component({
  selector: 'app-repuesto-form-page',
  standalone: true,
  imports: [EscanerCodigoComponent, ReactiveFormsModule, RouterLink, HlmButtonImports, HlmCardImports, HlmInputImports, HlmLabelImports],
  templateUrl: './repuesto-form.page.html',
})
export class RepuestoFormPage {
  private readonly servicio = inject(RepuestosService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);

  protected readonly config = REPUESTOS_CONFIG;
  protected readonly esDemo = environment.useMockData;
  protected readonly id = Number(inject(ActivatedRoute).snapshot.paramMap.get('id')) || null;
  protected readonly carga = signal<Carga>(this.id ? 'cargando' : 'listo');
  protected readonly guardando = signal(false);
  protected readonly error = signal<string | null>(null);

  protected readonly form = this.fb.nonNullable.group({
    codigo: ['', [Validators.required, Validators.pattern(/\S/), Validators.maxLength(100)]],
    nombre: ['', [Validators.required, Validators.pattern(/\S/), Validators.maxLength(200)]],
    descripcion: [''],
    stock_minimo: [0, [Validators.required, Validators.min(0), Validators.pattern(/^\d+$/)]],
    activo: [true],
  });

  constructor() {
    this.cargar();
  }

  protected cargar(): void {
    if (!this.id) return;
    this.carga.set('cargando');
    this.servicio
      .obtener(this.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (repuesto) => {
          this.form.reset({
            codigo: repuesto.codigo,
            nombre: repuesto.nombre,
            descripcion: repuesto.descripcion ?? '',
            stock_minimo: repuesto.stock_minimo,
            activo: repuesto.activo,
          });
          this.carga.set('listo');
        },
        error: () => this.carga.set('error'),
      });
  }

  protected invalido(campo: 'codigo' | 'nombre' | 'stock_minimo'): boolean {
    const control = this.form.controls[campo];
    return control.invalid && (control.touched || control.dirty);
  }

  protected codigoEscaneado(codigo: string): void {
    this.form.controls.codigo.setValue(codigo);
    this.form.controls.codigo.markAsDirty();
  }

  protected guardar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const valores = this.form.getRawValue();
    const datos = {
      codigo: valores.codigo.trim(),
      nombre: valores.nombre.trim(),
      descripcion: valores.descripcion.trim() || null,
      stock_minimo: Number(valores.stock_minimo),
    };
    const operacion: Observable<RepuestoDto> = this.id
      ? this.servicio.actualizar(this.id, { ...datos, activo: valores.activo })
      : this.servicio.crear(datos);

    this.guardando.set(true);
    this.error.set(null);
    operacion.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (repuesto) => {
        this.guardando.set(false);
        this.toast.show({
          variant: 'success',
          message: this.id ? this.config.formulario.actualizado : this.config.formulario.creado,
        });
        this.router.navigate(['/stock', repuesto.id]);
      },
      error: (respuesta: HttpErrorResponse) => {
        this.guardando.set(false);
        this.error.set(
          respuesta.status === 409
            ? this.config.formulario.duplicado
            : respuesta.status === 403
              ? this.config.formulario.sinPermiso
              : this.config.formulario.error,
        );
      },
    });
  }
}
