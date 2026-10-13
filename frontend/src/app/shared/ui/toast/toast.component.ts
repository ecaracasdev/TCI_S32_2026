import { Component, input, output } from '@angular/core';
import type { ToastMessage } from '@core/services/toast.service';

@Component({
  selector: 'app-toast',
  standalone: true,
  templateUrl: './toast.component.html',
  styleUrl: './toast.component.css',
})
export class ToastComponent {
  readonly toast = input.required<ToastMessage>();
  readonly dismiss = output<number>();

  protected close(): void {
    this.dismiss.emit(this.toast().id);
  }
}
