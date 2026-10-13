import { Component, inject } from '@angular/core';
import { ToastService } from '@core/services/toast.service';
import { ToastComponent } from './toast.component';

@Component({
  selector: 'app-toast-container',
  standalone: true,
  imports: [ToastComponent],
  templateUrl: './toast-container.component.html',
  styleUrl: './toast-container.component.css',
})
export class ToastContainerComponent {
  private readonly toastService = inject(ToastService);
  protected readonly toasts = this.toastService.toasts;

  protected dismiss(toastId: number): void {
    this.toastService.dismiss(toastId);
  }
}
