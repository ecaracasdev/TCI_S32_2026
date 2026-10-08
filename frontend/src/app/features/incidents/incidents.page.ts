import { Component, signal } from '@angular/core';

const INCIDENTS_CONFIG = {
  title: 'Reportar incidencia',
  description: 'Contanos qué pasó para que mantenimiento pueda responder cuanto antes.',
  tips: [
    { title: 'Identificá la máquina', text: 'Escaneá el código del equipo o ingresalo manualmente.' },
    { title: 'Agregá una foto', text: 'Una imagen ayuda a entender el problema antes de llegar.' },
    { title: 'Seguimiento inmediato', text: 'El equipo de mantenimiento recibe el aviso al reportar.' },
  ],
};

@Component({
  selector: 'app-incidents-page',
  standalone: true,
  templateUrl: './incidents.page.html',
  styleUrl: './incidents.page.css',
})
export class IncidentsPage {
  protected readonly config = INCIDENTS_CONFIG;
  protected readonly submitted = signal(false);
  protected readonly fileName = signal('');

  protected submit(event: Event): void {
    event.preventDefault();
    this.submitted.set(true);
  }

  protected selectPhoto(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    this.fileName.set(file?.name ?? '');
  }

  protected newReport(): void {
    this.submitted.set(false);
    this.fileName.set('');
  }
}
