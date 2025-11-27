export interface TiffLayer {
  name: string;        // Variable name (var_name) - used in tile URLs
  metricName: string;  // Metric name - needed for tile URLs and colormap lookup
  colormap?: string;   // Optional colormap identifier
  opacity?: number;    // Optional opacity setting
  isLoaded?: boolean;  // Optional loading state
}
