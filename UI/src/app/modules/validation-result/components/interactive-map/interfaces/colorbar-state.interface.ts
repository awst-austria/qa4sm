// interfaces/colorbar-state.interface.ts
export interface ColorbarState {
  gradient: string;
  vmin: number;
  vmax: number;
  metric_name: string;
  metrics_description?: string;
  is_categorical: boolean;
  legend_data?: { entries: LegendEntry[] };
  // Track whether the user has overridden the range
  isCustomRange: boolean;
}

export interface LegendData {
  entries: LegendEntry[];
}

export interface LegendEntry {
  value: number;
  label: string;
  color: string;
}