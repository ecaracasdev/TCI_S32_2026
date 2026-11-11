import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { environment } from '../../../environments/environment';
import { ESTADOS_MAQUINA, MAQUINAS_CONFIG } from './maquinas.config';
import { MaquinaDto } from './maquinas.models';
import { MaquinasService } from './maquinas.service';

type Carga = 'cargando' | 'listo' | 'error';

@Component({
  selector: 'app-maquina-detalle-page',
  standalone: true,
  imports: [RouterLink, HlmBadgeImports, HlmButtonImports, HlmCardImports],
  templateUrl: './maquina-detalle.page.html',
})
export class MaquinaDetallePage {
  private readonly servicio = inject(MaquinasService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly ruta = inject(ActivatedRoute);

  protected readonly config = MAQUINAS_CONFIG;
  protected readonly esDemo = environment.useMockData;
  protected readonly maquina = signal<MaquinaDto | null>(null);
  protected readonly carga = signal<Carga>('cargando');

  constructor() {
    this.cargar();
  }

  protected cargar(): void {
    const id = Number(this.ruta.snapshot.paramMap.get('id'));
    this.carga.set('cargando');
    this.servicio
      .obtenerPorId(id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (maquina) => {
          this.maquina.set(maquina);
          this.carga.set('listo');
        },
        error: () => this.carga.set('error'),
      });
  }

  protected estado(valor: string) {
    return ESTADOS_MAQUINA[valor] ?? { etiqueta: valor, variante: 'outline' as const };
  }

  protected fecha(valor: string | null | undefined): string {
    return valor ? new Date(valor).toLocaleString('es-AR') : this.config.detalle.noInformado;
  }
}
