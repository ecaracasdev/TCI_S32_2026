export type PreviewTone = 'danger' | 'warning' | 'good' | 'info';

export type PreviewIcon =
  | 'activity'
  | 'alert'
  | 'arrowLeft'
  | 'arrowRight'
  | 'arrowUpRight'
  | 'boxes'
  | 'check'
  | 'factory'
  | 'package';

export interface DashboardIncidentPreview {
  code: string;
  machine: string;
  issue: string;
  time: string;
  state: string;
  tone: PreviewTone;
  initials: string;
}

export interface DashboardStockPreview {
  name: string;
  code: string;
  available: number;
  minimum: number;
  tone: PreviewTone;
  location: string;
}

export interface DashboardPreview {
  incidents: DashboardIncidentPreview[];
  stock: DashboardStockPreview[];
}

export interface StockPartPreview {
  code: string;
  name: string;
  description: string;
  machines: string;
  physical: number;
  reserved: number;
  minimum: number;
  location: string;
  state: string;
  tone: PreviewTone;
}

export interface StockPreview {
  totalParts: number;
  purchaseListCount: number;
  reservedUnits: number;
  items: StockPartPreview[];
}

export interface MachinePreview {
  code: string;
  name: string;
  type: string;
  sector: string;
  status: string;
  tone: PreviewTone;
  incidents: number;
  lastReview: string;
  icon: PreviewIcon;
}

export interface MachinesPreview {
  items: MachinePreview[];
}

export interface GeneralPreview {
  dashboard: DashboardPreview;
  machines: MachinesPreview;
  stock: StockPreview;
}
