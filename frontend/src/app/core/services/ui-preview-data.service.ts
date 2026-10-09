import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { forkJoin, Observable } from 'rxjs';
import type { DashboardPreview, GeneralPreview, MachinesPreview, StockPreview } from '../models/ui-preview.models';

@Injectable({ providedIn: 'root' })
export class UiPreviewDataService {
  private readonly http = inject(HttpClient);

  getDashboard(): Observable<DashboardPreview> {
    return this.http.get<DashboardPreview>('/mock/ui-preview/dashboard.json');
  }

  getStock(): Observable<StockPreview> {
    return this.http.get<StockPreview>('/mock/ui-preview/stock.json');
  }

  getMachines(): Observable<MachinesPreview> {
    return this.http.get<MachinesPreview>('/mock/ui-preview/machines.json');
  }

  getGeneralPreview(): Observable<GeneralPreview> {
    return forkJoin({
      dashboard: this.getDashboard(),
      machines: this.getMachines(),
      stock: this.getStock(),
    });
  }
}
