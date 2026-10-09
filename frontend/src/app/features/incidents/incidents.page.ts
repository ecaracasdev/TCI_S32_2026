import { Component, ElementRef, computed, effect, inject, signal, viewChild } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmInputImports } from '@shared/ui/input';
import { HlmLabelImports } from '@shared/ui/label';
import { IconComponent } from '@shared/ui/icon';
import { UiPreviewDataService } from '@core/services/ui-preview-data.service';

const INCIDENTS_CONFIG = {
  title: 'Reportar incidencia',
  description: 'Identificá la máquina y contanos qué pasó.',
  machineLabel: 'Código de máquina',
  machinePlaceholder: 'Ej. FRAC-F02-001',
  scanLabel: 'Escanear código QR',
  reportLabel: 'Generar reporte',
  descriptionLabel: 'Descripción del problema',
  descriptionPlaceholder: 'Describí brevemente qué observaste…',
};

interface DetectedBarcode {
  rawValue: string;
}

interface NativeBarcodeDetector {
  detect(source: CanvasImageSource): Promise<DetectedBarcode[]>;
}

interface NativeBarcodeDetectorConstructor {
  new (options?: { formats: string[] }): NativeBarcodeDetector;
}

@Component({
  selector: 'app-incidents-page',
  standalone: true,
  imports: [HlmButtonImports, HlmCardImports, HlmBadgeImports, HlmInputImports, HlmLabelImports, IconComponent],
  templateUrl: './incidents.page.html',
  styleUrl: './incidents.page.css',
})
export class IncidentsPage {
  protected readonly config = INCIDENTS_CONFIG;
  protected readonly submitted = signal(false);
  protected readonly scannerOpen = signal(false);
  protected readonly cameraMessage = signal('');
  protected readonly reportDetailsOpen = signal(false);
  protected readonly photoDialogOpen = signal(false);
  protected readonly photoCount = signal(0);
  protected readonly machineCode = signal('');
  protected readonly scannerVideo = viewChild<ElementRef<HTMLVideoElement>>('scannerVideo');

  private readonly machinesPreview = toSignal(inject(UiPreviewDataService).getMachines(), { initialValue: null });
  protected readonly selectedMachine = computed(() => this.machinesPreview()?.items.find(
    (machine) => machine.code.toLowerCase() === this.machineCode().trim().toLowerCase(),
  ) ?? null);

  constructor() {
    effect((onCleanup) => {
      const isOpen = this.scannerOpen();
      const video = this.scannerVideo()?.nativeElement;
      if (!isOpen || !video) return;

      let stopped = false;
      let stream: MediaStream | undefined;
      let scanTimer = 0;
      onCleanup(() => {
        stopped = true;
        window.clearTimeout(scanTimer);
        stream?.getTracks().forEach((track) => track.stop());
        video.srcObject = null;
      });

      const Detector = (window as Window & { BarcodeDetector?: NativeBarcodeDetectorConstructor }).BarcodeDetector;
      if (!Detector || !navigator.mediaDevices?.getUserMedia) {
        this.cameraMessage.set('Este dispositivo no permite leer QR desde la cámara. Ingresá el código manualmente.');
        return;
      }

      this.cameraMessage.set('');
      void (async () => {
        try {
          stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false });
          if (stopped) {
            stream.getTracks().forEach((track) => track.stop());
            return;
          }
          video.srcObject = stream;
          await video.play();
          const detector = new Detector({ formats: ['qr_code'] });

          const scan = async (): Promise<void> => {
            if (stopped) return;
            try {
              const [barcode] = await detector.detect(video);
              if (barcode?.rawValue) {
                this.machineCode.set(this.machineCodeFromQr(barcode.rawValue));
                this.scannerOpen.set(false);
                return;
              }
            } catch {
              // La cámara sigue activa mientras se intenta leer otro fotograma.
            }
            if (!stopped) scanTimer = window.setTimeout(() => void scan(), 180);
          };

          void scan();
        } catch {
          this.cameraMessage.set('No se pudo abrir la cámara. Revisá el permiso o ingresá el código manualmente.');
        }
      })();
    });
  }

  protected updateMachineCode(event: Event): void {
    this.machineCode.set((event.target as HTMLInputElement).value);
  }

  protected toggleScanner(): void {
    this.cameraMessage.set('');
    this.scannerOpen.update((open) => !open);
  }

  protected openReportDetails(): void {
    if (this.selectedMachine()) this.reportDetailsOpen.set(true);
  }

  protected openPhotoDialog(): void {
    this.photoDialogOpen.set(true);
  }

  protected closePhotoDialog(): void {
    this.photoDialogOpen.set(false);
  }

  protected updatePhotoCount(event: Event): void {
    const files = (event.target as HTMLInputElement).files;
    if (files?.length) this.photoCount.update((count) => count + files.length);
    this.photoDialogOpen.set(false);
  }

  protected submit(event: Event): void {
    event.preventDefault();
    this.submitted.set(true);
  }

  protected newReport(): void {
    this.submitted.set(false);
    this.scannerOpen.set(false);
    this.reportDetailsOpen.set(false);
    this.photoDialogOpen.set(false);
    this.photoCount.set(0);
    this.machineCode.set('');
  }

  private machineCodeFromQr(value: string): string {
    try {
      const url = new URL(value);
      return decodeURIComponent(url.pathname.split('/').filter(Boolean).at(-1) ?? value).trim();
    } catch {
      return value.trim();
    }
  }
}
