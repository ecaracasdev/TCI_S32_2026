import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmInputImports } from '@shared/ui/input';
import { HlmLabelImports } from '@shared/ui/label';
import { ToastService } from '../../core/services/toast.service';
import { environment } from '../../../environments/environment';
import { REPORTAR_INCIDENCIA_CONFIG } from './reportar-incidencia.config';
import { FotoIncidenciaCreateDto, IncidenciaCreateDto, Turno } from './reportar-incidencia.models';
import { ReportarIncidenciaService } from './reportar-incidencia.service';

// TODO: el dominio no define los horarios de cada turno. Provisorio: 6-14 mañana, 14-22 tarde, 22-6 noche.
function turnoSegunHora(): Turno {
  const hora = new Date().getHours();
  if (hora >= 6 && hora < 14) return 'manana';
  if (hora >= 14 && hora < 22) return 'tarde';
  return 'noche';
}

@Component({
  selector: 'app-reportar-incidencia-page',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
  ],
  templateUrl: './reportar-incidencia.page.html',
})
export class ReportarIncidenciaPage {
  private readonly servicio = inject(ReportarIncidenciaService);
  private readonly toast = inject(ToastService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly fb = inject(FormBuilder);
  protected readonly config = REPORTAR_INCIDENCIA_CONFIG;
  protected readonly esDemo = environment.useMockData;
  protected readonly enviando = signal(false);
  protected readonly fotos = signal<FotoIncidenciaCreateDto[]>([]);

  protected readonly form = this.fb.nonNullable.group({
    maquina_codigo: ['', Validators.required],
    descripcion: ['', Validators.required],
    turno: [turnoSegunHora(), Validators.required],
  });

  protected escanear(): void {
    const codigos = this.config.maquina.codigosDemo;
    const codigo = codigos[Math.floor(Math.random() * codigos.length)];
    this.form.controls.maquina_codigo.setValue(codigo);
  }

  protected agregarFotos(evento: Event): void {
    const input = evento.target as HTMLInputElement;
    const archivos = Array.from(input.files ?? []);
    for (const archivo of archivos) {
      const lector = new FileReader();
      lector.onload = () => {
        const contenido = (lector.result as string).split(',')[1];
        this.fotos.update((lista) => [
          ...lista,
          {
            contenido_base64: contenido,
            nombre_archivo: archivo.name,
            tipo_mime: archivo.type,
            capturada_en: new Date(archivo.lastModified).toISOString(),
          },
        ]);
      };
      lector.readAsDataURL(archivo);
    }
    input.value = '';
  }

  protected quitarFoto(indice: number): void {
    this.fotos.update((lista) => lista.filter((_, i) => i !== indice));
  }

  protected enviar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.enviando.set(true);
    const datos: IncidenciaCreateDto = {
      ...this.form.getRawValue(),
      maquina_codigo: this.form.controls.maquina_codigo.value.trim(),
      fotos: this.fotos(),
    };
    this.servicio
      .crearIncidencia(datos)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.enviando.set(false);
          this.toast.show({
            variant: 'success',
            title: this.config.exito,
            message: this.esDemo ? this.config.demo : this.config.exito,
          });
          this.form.reset({ turno: turnoSegunHora() });
          this.fotos.set([]);
        },
        error: (error: { status?: number; message?: string }) => {
          this.enviando.set(false);
          this.toast.show({
            variant: 'error',
            title: this.config.errorGenerico,
            message:
              error.status === 404 ? this.config.maquina.noEncontrada : (error.message ?? ''),
          });
        },
      });
  }
}
