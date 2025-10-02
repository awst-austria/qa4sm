// interfaces/tiff-layer.interface.ts
export interface TiffLayer {
  index: number;
  description: string;
  bandName: string;
  minValue: number;
  maxValue: number;
  colormap: string;
  opacity?: number;
  url?: string;
  projection?: string;
  tileSize?: number;
}