// interactive-map.component.ts
import { Component, input, OnInit, Input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DropdownModule } from 'primeng/dropdown';
import { ButtonModule } from 'primeng/button';
import { MapModule } from '../../../map/map.module';
import { Map, View } from 'ol';
import TileLayer from 'ol/layer/Tile';
import { XYZ, TileWMS } from 'ol/source';
import { Cluster } from 'ol/source';
import VectorSource from 'ol/source/Vector';
import { FullScreen } from 'ol/control';
import { WebsiteGraphicsService } from '../../../core/services/global/website-graphics.service';
import { TiffLayer } from './interfaces/layer.interfaces';
import { ValidationrunDto } from '../../../core/services/validation-run/validationrun.dto';
import { MetricsPlotsDto } from '../../../core/services/validation-run/metrics-plots.dto';
import { LegendControl } from './legend-control/legend-control';
import { ValidationrunService } from '../../../core/services/validation-run/validationrun.service';

@Component({
  selector: 'qa-interactive-map',
  standalone: true,
  imports: [MapModule, CommonModule, FormsModule, DropdownModule, ButtonModule],
  templateUrl: './interactive-map.component.html',
  styleUrls: ['./interactive-map.component.scss']
})

export class InteractiveMapComponent implements OnInit {
  Object = Object;
  private httpClient = inject(HttpClient);
  validationId = input('');
  @Input() validationRun: ValidationrunDto;

  Map: Map;
  clusteredSource: VectorSource = new VectorSource();
  availableLayers: TiffLayer[] = [];
  currentLayer: TiffLayer | null = null;
  currentTileLayer: any = null;
  isLoading = false;
  cachedMetadata: any = null;
  selectedLayerForMetric: { [metric: string]: LayerDetail } = {};
  colorbarData: any = null;
  private legendControl: LegendControl | null = null;
  statusMetadata: any = null;
  selectedMetric: MetricsPlotsDto = {} as MetricsPlotsDto;
  metrics: MetricsPlotsDto[] = [];

  constructor(public plotService: WebsiteGraphicsService, private validationRunService: ValidationrunService) { }

  ngOnInit() {
    this.initMap();
    this.loadInitialMetric();
  }

  private loadMetadataAndInitializeLayers() {
    const geotiffMetrics = this.selectedMetric.geotiff_metrics || {};
    console.log('selectedMetric object:', this.selectedMetric);
    console.log('selectedMetric.geotiff_metrics:', this.selectedMetric.geotiff_metrics);

    this.plotService.getValidationMetadata(
      this.validationId(),
      geotiffMetrics
    ).subscribe({
      next: (metadata) => {
        console.log('Received metadata:', metadata);
        this.cachedMetadata = metadata;
        this.statusMetadata = metadata.status_metadata || {};

        if (!metadata.layer_mapping || Object.keys(metadata.layer_mapping).length === 0) {
          console.error('No layer_mapping found in metadata');
          return;
        }

        // Initialize default layer selections for each metric
        Object.keys(metadata.layer_mapping).forEach(metric => {
          const layerData = metadata.layer_mapping[metric];
          console.log(`Processing metric ${metric}:`, layerData);

          if (layerData && typeof layerData === 'object' && Object.keys(layerData).length > 0) {
            const layerKeys = Object.keys(layerData);

            if (layerKeys.length === 1) {
              const layerKey = layerKeys[0];
              const layerValue = layerData[layerKey];
              this.selectedLayerForMetric[metric] = {
                name: layerKey,
                index: parseInt(layerValue) || 0,
                metricName: metric,
              };
              console.log(`Single layer found for metric ${metric}:`, this.selectedLayerForMetric[metric]);
            } else if (layerKeys.length > 1) {
              const firstLayerKey = layerKeys[0];
              const firstLayerValue = layerData[firstLayerKey];
              this.selectedLayerForMetric[metric] = {
                name: firstLayerKey,
                index: parseInt(firstLayerValue) || 0,
                metricName: metric,
              };
              console.log(`Multiple layers found for metric ${metric}, using first:`, this.selectedLayerForMetric[metric]);
              console.log(`Available options for ${metric}:`, layerKeys);
            }
          } else {
            console.warn(`No valid layer data found for metric ${metric}`);
            this.selectedLayerForMetric[metric] = null;
          }
        });

        // Check current metric status and update both tile layer and legend
        if (this.selectedMetric) {
          const currentMetric = this.selectedMetric.metric_query_name;
          console.log(`Checking current metric: ${currentMetric}`);

          if (this.selectedLayerForMetric[currentMetric]) {
            console.log(`Current metric ${currentMetric} has selected layer:`, this.selectedLayerForMetric[currentMetric]);
            this.addTileLayerForMetric();
          } else {
            console.log(`Current metric ${currentMetric} has no selected layer - clearing display`);
            this.clearMapAndLegend();
          }
        }
        console.log('Final selectedLayerForMetric:', this.selectedLayerForMetric);
      },
      error: (error) => {
        console.error('Error loading metadata:', error);
        this.isLoading = false;
      }
    });
  }


  // Method to handle layer selection change
  onLayerSelectionChange(metric: string, selectedLayer: LayerDetail | null) {
    if (!selectedLayer) {
      console.warn(`No layer found for selection`);
      return;
    }

    console.log(`Layer selection changed for metric ${metric}:`, selectedLayer);
    this.selectedLayerForMetric[metric] = selectedLayer;

    // If this is the currently displayed metric, update the map (but not the legend)
    if (this.selectedMetric?.metric_query_name === metric) {
      console.log('Updating map for current metric');
      this.addTileLayerForMetric();
    }
  }
  onMetricChange(event: any): void {
    this.selectedMetric = event.value;

    // Trigger the same logic as ngOnChanges
    if (this.cachedMetadata) {
      if (this.selectedLayerForMetric[this.selectedMetric.metric_query_name]) {
        this.addTileLayerForMetric();
      } else {
        this.clearMapAndLegend();
      }
    } else {
      this.loadMetadataAndInitializeLayers();
    }
  }


  private initMap() {
    let clusterSource = new Cluster({
      source: this.clusteredSource,
      distance: 20
    });

    this.legendControl = new LegendControl({
      colorbarData: null,
      metricName: ''
    });

    this.Map = new Map({
      target: 'imap',
      layers: [
        new TileLayer({
          source: new TileWMS({
            url: 'https://tiles.maps.eox.at/wms',
            params: {
              'LAYERS': 'terrain-light',
              'TILED': true,
              'CRS': 'EPSG:4326'
            },
            serverType: 'geoserver',
            attributions: 'Data © OpenStreetMap contributors and others, Rendering © EOX'
          })
        })
      ],
      view: new View({
        projection: 'EPSG:4326',
        center: [0, 0],
        zoom: 2,
        minZoom: 0,
        maxZoom: 18
      }),
      controls: [new FullScreen(), this.legendControl]
    });
  }

  private addTileLayerForMetric() {
    const validationIdValue = this.validationId();
    console.log('addTileLayerForMetric - validationId:', validationIdValue);
    console.log('addTileLayerForMetric - selectedMetric:', this.selectedMetric);
    console.log('addTileLayerForMetric - cachedMetadata exists:', !!this.cachedMetadata);

    if (!validationIdValue || !this.selectedMetric) {
      console.error('No validationId or selectedMetric provided - cannot add tile layer');
      return;
    }

    if (!this.cachedMetadata) {
      console.warn('Metadata not loaded yet - cannot add tile layer');
      return;
    }

    this.isLoading = true;

    const currentMetric = this.selectedMetric.metric_query_name;
    const selectedLayer = this.selectedLayerForMetric[currentMetric];

    console.log('Current metric:', currentMetric);
    console.log('Selected layer for metric:', selectedLayer);
    console.log('All selectedLayerForMetric:', this.selectedLayerForMetric);

    if (selectedLayer) {
      const metricLayer: TiffLayer = {
        index: selectedLayer.index,
        description: selectedLayer.name || this.selectedMetric.metric_pretty_name || 'Metric Layer',
        metricName: selectedLayer.metricName,
        opacity: 0.7,
        isLoaded: false
      };

      console.log(`Adding tile layer for metric: ${this.selectedMetric.metric_pretty_name}, layer: ${selectedLayer.name}`);

      // Always add the tile layer
      this.updateTileLayer(metricLayer);

      // Always update colorbar for any metric with a tile layer
      this.updateVisualizationForCurrentMetric();

    } else {
      console.error(`No layer selected for metric: ${currentMetric}`);
      console.error('Available metrics in cachedMetadata:', Object.keys(this.cachedMetadata.metrics || {}));
    }

    this.isLoading = false;
  }


  isCurrentMetricStatus(): boolean {
    return this.selectedMetric?.metric_query_name === 'status';
  }
  getStatusLegendEntries(): any[] {
    if (!this.colorbarData || !this.colorbarData.legend_data) {
      return [];
    }
    return this.colorbarData.legend_data.entries || [];
  }

  // MODIFIED: Remove legend update logic from here
  private updateTileLayer(layer: TiffLayer) {
    if (this.currentTileLayer) {
      console.log('Removing existing tile layer');
      this.Map.removeLayer(this.currentTileLayer);
    }

    const validationIdValue = this.validationId();
    if (!validationIdValue) {
      console.error('No validationId for tile layer');
      return;
    }

    const tileUrl = `/api/${validationIdValue}/tiles/${layer.metricName}/${layer.index}/{z}/{x}/{y}.png`;
    console.log(`Creating tile layer with URL: ${tileUrl}`);

    this.currentTileLayer = new TileLayer<XYZ>({
      source: new XYZ({
        url: tileUrl,
        tileSize: 256,
        projection: 'EPSG:3857'
      }),
      opacity: layer.opacity || 0.7
    });

    this.Map.addLayer(this.currentTileLayer);
    this.currentLayer = layer;
    console.log(`Successfully added tile layer for index ${layer.index}`);

  }

  private updateVisualizationForCurrentMetric() {
    if (!this.selectedMetric || !this.cachedMetadata) {
      console.warn('No selectedMetric or cachedMetadata for visualization update');
      this.clearMapAndLegend();
      return;
    }

    const currentMetric = this.selectedMetric.metric_query_name;
    const selectedLayer = this.selectedLayerForMetric[currentMetric];

    if (!selectedLayer) {
      console.log(`No layer selected for metric: ${currentMetric}`);
      this.clearMapAndLegend();
      return;
    }

    console.log(`Updating visualization for metric: ${currentMetric}, layer: ${selectedLayer.name}`);

    // Get colormap metadata from cached metadata (instant)
    const colormapMetadata = this.cachedMetadata.colormap_metadata?.[currentMetric];

    // Lazy-load vmin/vmax
    this.plotService.getLayerRange(
      this.validationId(),
      currentMetric,
      selectedLayer.index
    ).subscribe({
      next: (rangeData) => {
        // Combine colormap metadata + range data
        const completeColormap = {
          ...colormapMetadata,
          vmin: rangeData.vmin,
          vmax: rangeData.vmax,
          metric_name: currentMetric
        };

        // Decide: colorbar or legend?
        if (colormapMetadata.is_categorical) {
          // Show legend for categorical data (e.g., status)
          this.showLegend(completeColormap, selectedLayer);
        } else {
          // Show colorbar for continuous data
          this.showColorbar(completeColormap);
        }

        // Store for tile rendering and template access
        this.colorbarData = completeColormap;
      },
      error: (error) => {
        console.error('Error fetching layer range:', error);
      }
    });
  }

  // Helper method to get available layers for current metric
  getAvailableLayersForCurrentMetric(): LayerDetail[] {
    if (!this.cachedMetadata || !this.selectedMetric) {
      console.log('No cached metadata or selected metric for layers');
      return [];
    }

    const metricData = this.cachedMetadata.layer_mapping[this.selectedMetric.metric_query_name];
    if (!metricData) {
      console.log(`No layer data found for metric: ${this.selectedMetric.metric_query_name}`);
      return [];
    }

    const layers: LayerDetail[] = Object.keys(metricData).map(layerName => ({
      name: layerName,
      index: parseInt(metricData[layerName]) || 0,
      metricName: this.selectedMetric.metric_query_name,
    }));

    return layers;
  }

  currentMetricHasMultipleLayers(): boolean {
    if (!this.cachedMetadata || !this.selectedMetric) return false;

    const metricData = this.cachedMetadata.layer_mapping[this.selectedMetric.metric_query_name];
    return metricData ? Object.keys(metricData).length > 1 : false;
  }

  getLayerByName(layerName: string): LayerDetail | null {
    const availableLayers = this.getAvailableLayersForCurrentMetric();
    return availableLayers.find(layer => layer.name === layerName) || null;
  }

  resetMapView() {
    if (this.Map) {
      this.Map.getView().animate({
        center: [0, 0],
        zoom: 2,
        duration: 1000
      });
    }
  }

  getColorbarData(metricName: string, index: number): Observable<any> {
    const validationId = this.validationId();
    return this.httpClient.get(`/api/${validationId}/colorbar/${metricName}/${index}/`);
  }

  getColorbarGradient(): string {
    return this.colorbarData?.gradient || 'linear-gradient(to right, blue, cyan, yellow, red)';
  }

  getColorbarMin(): string {
    return this.colorbarData?.vmin?.toFixed(2) || '0.0';
  }

  getColorbarMax(): string {
    return this.colorbarData?.vmax?.toFixed(2) || '1.0';
  }
  // NEW METHOD: Clear map and legend
  private clearMapAndLegend() {
    if (this.currentTileLayer) {
      this.Map.removeLayer(this.currentTileLayer);
      this.currentTileLayer = null;
      this.currentLayer = null;
    }
    if (this.legendControl) {
      this.legendControl.updateLegend(null, '');
    }
    this.colorbarData = null;
  }
  private showColorbar(colorbarData: any) {
    console.log('Showing colorbar for continuous data:', colorbarData);

    // Hide legend
    if (this.legendControl) {
      this.legendControl.updateLegend(null, '');
    }

    // Store colorbar data (your template already uses this)
    this.colorbarData = colorbarData;
  }

  private showLegend(colorbarData: any, selectedLayer: LayerDetail) {
    console.log('Showing legend for categorical data:', colorbarData);

    // Get status legend entries from cached metadata
    const statusLegend = this.cachedMetadata.status_metadata?.[selectedLayer.name];

    if (statusLegend && this.legendControl) {
      // Combine colorbar data with status legend entries
      const legendData = {
        ...colorbarData,
        legend_data: statusLegend
      };

      this.legendControl.updateLegend(legendData, selectedLayer.metricName);

      // Store for template access (if needed)
      this.colorbarData = legendData;
    } else {
      console.warn('No status legend data found for layer:', selectedLayer.name);
      // Fallback: clear legend
      if (this.legendControl) {
        this.legendControl.updateLegend(null, '');
      }
    }
  }


  private loadInitialMetric(): void {
    const params = new HttpParams().set('validationId', this.validationId());
    this.validationRunService.getMetricsAndPlotsNames(params)
      .subscribe({
        next: (metrics) => {
          this.metrics = metrics;  // Store the array

          if (metrics.length > 0) {
            this.selectedMetric = metrics[0];  // Set first as default
            this.loadMetadataAndInitializeLayers();
          }
        },
        error: (error) => console.error('Error loading metrics:', error)
      });
  }
}

export interface LayerDetail {
  name: string;
  index: number;
  metricName: string;
}

export interface ValidationMetadata {
  validation_id: string;
  layer_mapping: { [metric: string]: { [layerName: string]: string } };
}

