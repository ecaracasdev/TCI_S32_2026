import { Component, ElementRef, OnDestroy, output, signal, viewChild } from '@angular/core';
import { HlmButtonImports } from '@shared/ui/button';

type Detector = { detect(video: HTMLVideoElement): Promise<{ rawValue: string }[]> };
type DetectorConstructor = new () => Detector;

/** Lectura con la cámara del navegador; el campo manual sigue disponible si no es compatible. */
@Component({
  selector: 'app-escaner-codigo',
  standalone: true,
  imports: [HlmButtonImports],
  template: `
    <button hlmBtn type="button" variant="outline" (click)="abrir()" [disabled]="abierto()">
      Escanear
    </button>
    @if (abierto()) {
      <div class="flex flex-col items-start gap-2">
        <video #video autoplay playsinline muted class="w-full max-w-sm rounded border" aria-label="Vista de la cámara"></video>
        <button hlmBtn type="button" variant="outline" (click)="cerrar()">Cancelar escaneo</button>
      </div>
    }
    @if (error()) { <p role="alert" class="text-sm text-destructive">{{ error() }}</p> }
  `,
})
export class EscanerCodigoComponent implements OnDestroy {
  readonly codigoLeido = output<string>();
  protected readonly abierto = signal(false);
  protected readonly error = signal('');
  private readonly video = viewChild<ElementRef<HTMLVideoElement>>('video');
  private stream: MediaStream | null = null;
  private frame = 0;
  private version = 0;

  protected async abrir(): Promise<void> {
    this.error.set('');
    const Detector = (globalThis as typeof globalThis & { BarcodeDetector?: DetectorConstructor }).BarcodeDetector;
    if (!Detector || !navigator.mediaDevices?.getUserMedia) {
      this.error.set('El navegador no admite escaneo con cámara. Ingresá el código manualmente.');
      return;
    }
    const version = ++this.version;
    this.abierto.set(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
      if (version !== this.version) { stream.getTracks().forEach((track) => track.stop()); return; }
      this.stream = stream;
      // Esperar al render del video antes de conectar la cámara.
      this.frame = requestAnimationFrame(async () => {
        const video = this.video()?.nativeElement;
        if (!video || version !== this.version) return;
        video.srcObject = stream;
        try {
          await video.play();
          await this.detectar(new Detector(), video, version);
        } catch {
          if (version === this.version) this.fallar('No se pudo iniciar la cámara. Ingresá el código manualmente.');
        }
      });
    } catch {
      if (version === this.version) this.fallar('No se pudo acceder a la cámara. Revisá los permisos o ingresá el código manualmente.');
    }
  }

  private async detectar(detector: Detector, video: HTMLVideoElement, version: number): Promise<void> {
    if (version !== this.version) return;
    try {
      const resultados = video.readyState >= 2 ? await detector.detect(video) : [];
      if (version !== this.version) return;
      const codigo = resultados.find((resultado) => resultado.rawValue.trim())?.rawValue;
      if (codigo) { this.codigoLeido.emit(codigo); this.cerrar(); return; }
      this.frame = requestAnimationFrame(() => void this.detectar(detector, video, version));
    } catch {
      if (version === this.version) this.fallar('No se pudo leer el código. Ingresalo manualmente.');
    }
  }

  private fallar(mensaje: string): void { this.cerrar(); this.error.set(mensaje); }
  protected cerrar(): void {
    this.version++;
    cancelAnimationFrame(this.frame);
    this.stream?.getTracks().forEach((track) => track.stop());
    this.stream = null;
    this.abierto.set(false);
  }
  ngOnDestroy(): void { this.cerrar(); }
}
