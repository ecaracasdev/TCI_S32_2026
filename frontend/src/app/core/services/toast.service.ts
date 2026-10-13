import { Injectable, signal } from '@angular/core';

export type ToastVariant = 'info' | 'success' | 'warning' | 'error';

export interface ToastOptions {
  message: string;
  title?: string;
  variant?: ToastVariant;
  duration?: number;
}

export interface ToastMessage {
  id: number;
  message: string;
  title?: string;
  variant: ToastVariant;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  private readonly toastState = signal<readonly ToastMessage[]>([]);
  private readonly timers = new Map<number, ReturnType<typeof setTimeout>>();
  private nextId = 0;

  readonly toasts = this.toastState.asReadonly();

  show(options: ToastOptions): number {
    const id = this.nextId++;
    const { duration = 4000, ...content } = options;
    const toast: ToastMessage = {
      ...content,
      id,
      variant: content.variant ?? 'info',
    };

    this.toastState.update((toasts) => [...toasts, toast]);

    if (duration > 0) {
      this.timers.set(id, setTimeout(() => this.dismiss(id), duration));
    }

    return id;
  }

  dismiss(id: number): void {
    const timer = this.timers.get(id);
    if (timer) clearTimeout(timer);
    this.timers.delete(id);
    this.toastState.update((toasts) => toasts.filter((toast) => toast.id !== id));
  }

  clear(): void {
    for (const timer of this.timers.values()) clearTimeout(timer);
    this.timers.clear();
    this.toastState.set([]);
  }
}
