export interface LayerMetadata {
  index: number;
  description: string;
}

export interface TiffLayer extends LayerMetadata {
  metricName: string;  // Key for _colormaps lookup in backend
  colormap?: string;   // Optional - could be derived from metricName
  opacity?: number;
  isLoaded?: boolean;
}