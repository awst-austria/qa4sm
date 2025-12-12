// interactive-map.component.ts
import { Component, input, Input, inject, AfterViewInit, ChangeDetectorRef, OnDestroy, ViewChild, ElementRef, HostListener } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { MapModule } from '../../../map/map.module';
import { Map, View, MapBrowserEvent } from 'ol';
import TileLayer from 'ol/layer/Tile';
import TileGrid from 'ol/tilegrid/TileGrid';
import { XYZ, TileWMS } from 'ol/source';
import VectorSource from 'ol/source/Vector';
import { transformExtent } from 'ol/proj'
import { FullScreen, Control } from 'ol/control';
import { SharedPrimeNgModule } from '../../../../shared.primeNg.module';
import { WebsiteGraphicsService } from '../../../core/services/global/website-graphics.service';
import { TiffLayer } from './interfaces/layer.interfaces';
import { ValidationrunDto } from '../../../core/services/validation-run/validationrun.dto';
import { MetricsPlotsDto } from '../../../core/services/validation-run/metrics-plots.dto';
import { LegendControl } from './legend-control/legend-control';
import { ValidationrunService } from '../../../core/services/validation-run/validationrun.service';
import { Popover } from 'primeng/popover';


@Component({
  selector: 'qa-interactive-map',
  standalone: true,
  imports: [
    MapModule,
    SharedPrimeNgModule,
    Popover
  ],
  templateUrl: './interactive-map.component.html',
  styleUrls: ['./interactive-map.component.scss']
})

export class InteractiveMapComponent implements AfterViewInit, OnDestroy {
  @ViewChild('metricDropdownContainer') metricDropdownContainer!: ElementRef;
  @ViewChild('layerDropdownContainer') layerDropdownContainer!: ElementRef;
  @ViewChild('snapshotButtonContainer') snapshotButtonContainer!: ElementRef;
  @ViewChild('projectionToggleContainer') projectionToggleContainer!: ElementRef;
  @ViewChild('mapContainer', { static: false }) mapContainer!: ElementRef;

  Object = Object;
  private httpClient = inject(HttpClient);
  validationId = input('');
  @Input() validationRun: ValidationrunDto;
  // Inject ChangeDetectorRef
  private cdr = inject(ChangeDetectorRef);

  Map: Map;
  clusteredSource: VectorSource = new VectorSource();
  availableLayers: TiffLayer[] = [];
  currentLayer: TiffLayer | null = null;
  currentTileLayer: any = null;
  isLoading = false;
  private currentLayerKey: string = '';
  cachedMetadata: any = null;
  selectedLayerForMetric: { [metric: string]: LayerDetail } = {};
  colorbarData: any = null;
  private legendControl: LegendControl | null = null;
  statusMetadata: any = null;
  selectedMetric: MetricsPlotsDto = {} as MetricsPlotsDto;
  metrics: MetricsPlotsDto[] = [];
  public currentProjection: 'EPSG:4326' | 'EPSG:3857' = 'EPSG:4326';
  private baseLayer4326!: TileLayer<TileWMS>;
  private baseLayer3857!: TileLayer<XYZ>;
  private shouldFitToBounds = true;
  showSnapshotModal = false;
  snapshotImageSrc: string | null = null;
  isFullscreen: boolean = false;
  clickedPointData: any = null;
  isLoadingPointData = false;
  pointPopupVisible = false;
  // Point query state
  selectedPointValue: string | null = null;
  selectedPointCoords: { lat: number; lon: number } | null = null;
  pointQueryLoading: boolean = false;
  snapshotTitle: string = 'Snapshot';



  constructor(public plotService: WebsiteGraphicsService, private validationRunService: ValidationrunService) { }



  ngAfterViewInit() {
    // now the template exists, safe to build OpenLayers Map
    this.initMap();
    this.loadInitialMetric();
    this.addAngularControlsToMap();
    document.addEventListener('fullscreenchange', () => {
      this.isFullscreen = document.fullscreenElement !== null;
      this.cdr.detectChanges();
    });

  }

  ngOnDestroy() {
    if (this.Map) {
      this.Map.dispose();
    }
    document.removeEventListener('fullscreenchange', () => { });
  }

  private setupMapClickHandler() {
    this.Map.on('singleclick', (event: MapBrowserEvent<any>) => {
      this.onMapClick(event);
    });
  }


  private loadMetadataAndInitializeLayers() {
    const zarrMetrics = this.selectedMetric.zarr_metrics || {};

    this.plotService.getValidationMetadata(
      this.validationId(),
      zarrMetrics
    ).subscribe({
      next: (metadata) => {
        console.log('Received metadata:', metadata);
        this.cachedMetadata = metadata;
        this.statusMetadata = metadata.status_metadata || {};

        if (!metadata.layers || metadata.layers.length === 0) {
          console.error('No layers found in metadata');
          this.isLoading = false;
          this.cdr.detectChanges(); // Force detection
          return;
        }

        metadata.layers.forEach(layer => {
          const metric = layer.metric;
          if (!this.selectedLayerForMetric[metric]) {
            this.selectedLayerForMetric[metric] = {
              name: layer.name,
              metricName: metric,
              colormap: layer.colormap
            };
          }
        });

        if (this.selectedMetric) {
          const currentMetric = this.selectedMetric.metric_query_name;
          if (this.selectedLayerForMetric[currentMetric]) {
            this.isLoading = false;
            this.cdr.detectChanges(); // Force detection
            this.addTileLayerForMetric();
          } else {
            this.clearMapAndLegend();
          }
        } else {
          this.isLoading = false;
          this.cdr.detectChanges(); // Force detection
        }
      },
      error: (error) => {
        console.error('Error loading metadata:', error);
        this.isLoading = false;
        this.cdr.detectChanges(); // Force detection
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
    console.log('[onMetricChange] Metric changed to:', event.value);
    this.shouldFitToBounds = false;
    this.selectedMetric = event.value;

    if (this.cachedMetadata) {
      if (this.selectedLayerForMetric[this.selectedMetric.metric_query_name]) {
        this.addTileLayerForMetric(); // This calls updateTileLayer which handles spinner
      } else {
        this.clearMapAndLegend();
      }
    } else {
      this.isLoading = true; // Only show for metadata loading
      this.loadMetadataAndInitializeLayers();
    }
  }

  private initMap() {
    console.log('[initMap] initializing map...');

    // 1. Define EOX WMS base layer (EPSG:4326)
    this.baseLayer4326 = new TileLayer({
      source: new TileWMS({
        url: 'https://tiles.maps.eox.at/wms',
        params: {
          LAYERS: 'terrain-light',
          TILED: true,
          CRS: 'EPSG:4326'
        },
        serverType: 'geoserver',
        attributions: 'Data © OpenStreetMap contributors and others, Rendering © EOX',
        crossOrigin: 'anonymous' //added for snapshot feature
      }),
      visible: true, // start with this
    });

    // 2. Define OSM base layer (EPSG:3857)
    this.baseLayer3857 = new TileLayer({
      source: new XYZ({
        url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        attributions: '© OpenStreetMap contributors',
        crossOrigin: 'anonymous' //added for snapshot feature
      }),
      visible: false // hidden initially
    });

    // 3. Initial view (use EPSG:4326 for now)
    const initialView = new View({
      projection: 'EPSG:4326',
      center: [0, 0],
      zoom: 2,
      minZoom: 0,
      maxZoom: 15
    });

    // 4. Construct map
    this.Map = new Map({
      target: 'imap',
      layers: [this.baseLayer4326, this.baseLayer3857],
      view: initialView,
      controls: [new FullScreen()]
    });
    this.legendControl = new LegendControl({
      colorbarData: null,
      metricName: ''
    });
    this.Map.addControl(this.legendControl);
    this.setupMapClickHandler();

    console.log('[initMap] map created with EOX base layer visible');
  }

  private addAngularControlsToMap(): void {
    if (!this.Map) {
      console.error('Map not initialized');
      return;
    }

    const metricElement = this.metricDropdownContainer.nativeElement;
    const layerElement = this.layerDropdownContainer.nativeElement;
    const snapshotElement = this.snapshotButtonContainer.nativeElement;
    const projectionElement = this.projectionToggleContainer.nativeElement;

    metricElement.style.display = 'block';
    layerElement.style.display = 'block';
    snapshotElement.style.display = 'block';
    projectionElement.style.display = 'block';

    const metricControl = new AngularControl(metricElement);
    const layerControl = new AngularControl(layerElement);
    const snapshotControl = new AngularControl(snapshotElement);
    const projectionControl = new AngularControl(projectionElement);

    this.Map.addControl(metricControl);
    this.Map.addControl(layerControl);
    this.Map.addControl(snapshotControl);
    this.Map.addControl(projectionControl);

    console.log('[addAngularControlsToMap] Controls added to map');
  }


  takeSnapshot(): void {
    console.log('[takeSnapshot] Button clicked');

    if (!this.Map) {
      console.error('Map not initialized');
      return;
    }

    console.log('[takeSnapshot] Fullscreen:', this.isFullscreen);

    const captureMap = () => {
      console.log('[takeSnapshot] Starting capture...');

      try {
        const mapCanvas = document.createElement('canvas');
        const size = this.Map!.getSize();
        if (!size) {
          console.error('Could not get map size');
          return;
        }

        console.log('[takeSnapshot] Canvas size:', size);
        mapCanvas.width = size[0];
        mapCanvas.height = size[1];
        const mapContext = mapCanvas.getContext('2d');
        if (!mapContext) {
          console.error('Could not get canvas context');
          return;
        }

        const canvases = document.querySelectorAll('#imap .ol-layer canvas');
        console.log('[takeSnapshot] Found canvases:', canvases.length);

        Array.prototype.forEach.call(
          canvases,
          (canvas: HTMLCanvasElement) => {
            if (canvas.width > 0) {
              const opacity = (canvas.parentNode as HTMLElement).style.opacity;
              mapContext.globalAlpha = opacity === '' ? 1 : Number(opacity);
              const transform = canvas.style.transform;
              const matrix = transform.match(/^matrix\(([^\(]*)\)$/);
              if (matrix) {
                mapContext.setTransform.apply(mapContext, matrix[1].split(',').map(Number) as any);
              }
              mapContext.drawImage(canvas, 0, 0);
            }
          }
        );

        mapContext.globalAlpha = 1;
        mapContext.setTransform(1, 0, 0, 1, 0, 0);

        // Add colorbar or legend based on data type
        if (this.colorbarData) {
          const isCategorical = this.colorbarData.is_categorical === true;

          if (isCategorical) {
            console.log('[takeSnapshot] Adding legend for categorical data');
            this.drawLegendOnCanvas(mapContext, mapCanvas);
          } else {
            console.log('[takeSnapshot] Adding colorbar for continuous data');
            this.drawColorbarOnCanvas(mapContext, mapCanvas);
          }
        }

        this.snapshotImageSrc = mapCanvas.toDataURL('image/png');


        if (this.currentLayerKey) {
          this.snapshotTitle = this.currentLayerKey.replace(/:/g, '');
        } else if (this.selectedMetric?.metric_pretty_name) {
          this.snapshotTitle = this.selectedMetric.metric_pretty_name;
        } else {
          this.snapshotTitle = 'Snapshot';
        }
        this.showSnapshotModal = true;
        // Force Angular change detection
        this.cdr.detectChanges();

        console.log('[takeSnapshot] Modal should now be visible');

      } catch (error) {
        console.error('Error capturing snapshot:', error);
        alert('Unable to capture snapshot. The map may contain protected content.');
      }
    };

    if (this.isFullscreen) {
      console.log('[takeSnapshot] Exiting fullscreen...');
      document.exitFullscreen().then(() => {
        setTimeout(captureMap, 300);
      }).catch((err) => {
        console.error('Error exiting fullscreen:', err);
        captureMap();
      });
    } else {
      console.log('[takeSnapshot] Normal mode - capturing immediately');
      captureMap();
    }
  }

  private drawLegendOnCanvas(ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement): void {
    console.log('drawLegendOnCanvas called with colorbarData:', this.colorbarData);

    if (!this.colorbarData) {
      console.warn('No colorbarData available');
      return;
    }

    if (!this.colorbarData.legend_data) {
      console.warn('No legend_data in colorbarData:', this.colorbarData);
      return;
    }

    if (!this.colorbarData.legend_data.entries) {
      console.warn('No entries in legend_data:', this.colorbarData.legend_data);
      return;
    }

    const entries = this.colorbarData.legend_data.entries;
    console.log('Drawing legend with entries:', entries);

    const padding = 20;
    const itemHeight = 24;
    const symbolSize = 16;
    const gap = 8;
    const titleHeight = 30;  // Increased from 25 to give more space
    const separatorGap = 8;  // Gap between separator and first item

    // Calculate dimensions
    const maxLabelWidth = 180;
    const legendWidth = symbolSize + gap + maxLabelWidth + padding * 2;
    const legendHeight = titleHeight + separatorGap + (entries.length * itemHeight) + padding;

    // Position in bottom-right corner
    const x = canvas.width - legendWidth - 20;
    const y = canvas.height - legendHeight - 20;

    // Draw background with border
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.fillRect(x, y, legendWidth, legendHeight);
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.15)';
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, legendWidth, legendHeight);

    // Draw title
    ctx.fillStyle = '#2c3e50';
    ctx.font = 'bold 13px Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(
      this.colorbarData.metric_name || 'Status',
      x + legendWidth / 2,
      y + padding + 10  // Adjusted vertical position
    );

    // Draw separator line (lower position)
    const separatorY = y + padding + 18;  // Position separator below title
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x + padding, separatorY);
    ctx.lineTo(x + legendWidth - padding, separatorY);
    ctx.stroke();

    // Draw legend items (start after separator + gap)
    ctx.font = '11px Arial, sans-serif';
    ctx.textAlign = 'left';

    entries.forEach((entry: any, index: number) => {
      const itemY = separatorY + separatorGap + (index * itemHeight);

      // Draw color symbol
      ctx.fillStyle = entry.color;
      ctx.fillRect(
        x + padding,
        itemY,
        symbolSize,
        symbolSize
      );

      // Draw symbol border
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
      ctx.lineWidth = 1;
      ctx.strokeRect(
        x + padding,
        itemY,
        symbolSize,
        symbolSize
      );

      // Draw label (vertically centered with symbol)
      ctx.fillStyle = '#34495e';
      ctx.fillText(
        entry.label,
        x + padding + symbolSize + gap,
        itemY + symbolSize / 2 + 4  // Center text vertically with symbol
      );
    });

    console.log('Legend drawn successfully');
  }






  // KEEP THIS METHOD AS IS
  private drawColorbarOnCanvas(ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement): void {
    const padding = 20;
    const barHeight = 20;
    const barWidth = Math.min(400, canvas.width - padding * 2);
    const x = (canvas.width - barWidth) / 2;
    const y = canvas.height - 60;

    // Background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.fillRect(0, canvas.height - 70, canvas.width, 70);

    // Draw gradient bar
    const gradient = ctx.createLinearGradient(x, y, x + barWidth, y);
    const colors = this.parseGradientColors(this.colorbarData.gradient);
    colors.forEach((color, index) => {
      gradient.addColorStop(index / (colors.length - 1), color);
    });

    ctx.fillStyle = gradient;
    ctx.fillRect(x, y, barWidth, barHeight);
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, barWidth, barHeight);

    // Draw text
    ctx.fillStyle = '#2c3e50';
    ctx.font = '12px Arial, sans-serif';

    // Min value
    ctx.textAlign = 'left';
    ctx.fillText(this.colorbarData.vmin.toFixed(1), x, y + barHeight + 15);

    // Title
    ctx.textAlign = 'center';
    ctx.font = 'bold 13px Arial, sans-serif';
    ctx.fillText(this.colorbarData.metric_name, canvas.width / 2, y + barHeight + 15);

    // Max value
    ctx.textAlign = 'right';
    ctx.font = '12px Arial, sans-serif';
    ctx.fillText(this.colorbarData.vmax.toFixed(1), x + barWidth, y + barHeight + 15);
  }

  private parseGradientColors(gradientString: string): string[] {
    const colorRegex = /#[0-9a-f]{6}|rgb\([^)]+\)|rgba\([^)]+\)/gi;
    const matches = gradientString.match(colorRegex);
    return matches || ['#ffffff', '#000000'];
  }


  downloadSnapshot(): void {
    if (!this.snapshotImageSrc) return;

    const link = document.createElement('a');
    const filename = this.snapshotTitle.replace(/[^a-z0-9]/gi, '-').toLowerCase() || 'map-snapshot';

    link.download = `${filename}.png`;
    link.href = this.snapshotImageSrc;
    link.click();
  }

  closeSnapshotModal(): void {
    this.showSnapshotModal = false;
    this.snapshotImageSrc = null;
  }

  closeModal(event: MouseEvent): void {
    if ((event.target as HTMLElement).classList.contains('snapshot-modal')) {
      this.closeSnapshotModal();
    }
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

    const currentMetric = this.selectedMetric.metric_query_name;
    const selectedLayer = this.selectedLayerForMetric[currentMetric];

    console.log('Current metric:', currentMetric);
    console.log('Selected layer for metric:', selectedLayer);
    console.log('All selectedLayerForMetric:', this.selectedLayerForMetric);

    if (selectedLayer) {
      const metricLayer: TiffLayer = {
        name: selectedLayer.name || this.selectedMetric.metric_pretty_name || 'Metric Layer',
        metricName: selectedLayer.metricName,
        opacity: 0.7,
        isLoaded: false
      };

      console.log(`Adding tile layer for metric: ${this.selectedMetric.metric_pretty_name}, layer: ${selectedLayer.name}`);
      console.log(`Using projection: ${this.currentProjection}`); // ADD: helpful debug log

      // FIX: Always pass the current projection
      this.updateTileLayer(metricLayer, this.currentProjection);

      // Always update colorbar for any metric with a tile layer
      this.updateVisualizationForCurrentMetric();

    } else {
      console.error(`No layer selected for metric: ${currentMetric}`);
      console.error('Available metrics in cachedMetadata:', Object.keys(this.cachedMetadata.metrics || {}));
    }
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
  // helper to create resolutions and tileGrid depending on projection
  private createTileGridForProjection(projection: 'EPSG:4326' | 'EPSG:3857') {
    if (projection === 'EPSG:4326') {
      const resolutions: number[] = [];
      for (let z = 0; z <= 18; z++) {
        resolutions[z] = 180 / (256 * Math.pow(2, z));
      }
      return new TileGrid({
        extent: [-180, -90, 180, 90],
        origin: [-180, 90],
        resolutions,
        tileSize: 256
      });
    } else {
      // WebMercator / EPSG:3857 tile grid (global)
      const WEBMERCATOR_EXTENT = [-20037508.342789244, -20037508.342789244, 20037508.342789244, 20037508.342789244];
      const origin: [number, number] = [WEBMERCATOR_EXTENT[0], WEBMERCATOR_EXTENT[3]];
      const initialResolution = 156543.03392804097; // resolution at zoom 0 for 256 tiles
      const resolutions: number[] = [];
      for (let z = 0; z <= 18; z++) {
        resolutions[z] = initialResolution / Math.pow(2, z);
      }
      return new TileGrid({
        extent: WEBMERCATOR_EXTENT,
        origin,
        resolutions,
        tileSize: 256
      });
    }
  }


  private async updateTileLayer(
    layer: TiffLayer,
    projection: 'EPSG:4326' | 'EPSG:3857' = 'EPSG:4326',
    fitToBounds: boolean = false
  ) {
    const layerKey = `${layer.metricName}_${layer.name}_${projection}`;
    console.log(`[updateTileLayer] Starting update for ${layerKey}`);

    const isNewLayer = this.currentLayerKey !== layerKey;

    if (isNewLayer) {
      this.currentLayerKey = layerKey;
      this.isLoading = true;
      console.log(`[updateTileLayer] Set isLoading = true for new layer`);
    }

    if (this.currentTileLayer) {
      this.Map.removeLayer(this.currentTileLayer);
    }

    const validationIdValue = this.validationId();
    if (!validationIdValue) {
      console.error('[updateTileLayer] No validationId for tile layer');
      this.isLoading = false;
      this.cdr.detectChanges(); // Force detection
      return;
    }

    const epsgCode = projection.replace('EPSG:', '');
    const tileUrl = `/api/${validationIdValue}/tiles/${layer.metricName}/${layer.name}/${epsgCode}/{z}/{x}/{y}.png`;

    const tileGrid = this.createTileGridForProjection(projection);

    this.currentTileLayer = new TileLayer({
      source: new XYZ({
        url: tileUrl,
        tileSize: 256,
        projection: projection,
        tileGrid: tileGrid
      }),
      opacity: layer.opacity ?? 0.7
    });

    const source = this.currentTileLayer.getSource();

    let firstTileReceived = false;

    const hideSpinner = () => {
      if (!firstTileReceived && this.isLoading) {
        firstTileReceived = true;
        console.log('[updateTileLayer] ✓ First tile received, hiding spinner NOW');
        this.isLoading = false;

        // THIS IS THE KEY FIX - Force Angular to detect the change
        this.cdr.detectChanges();

        console.log(`[updateTileLayer] isLoading set to: ${this.isLoading}`);

        // Clean up listeners
        source.un('tileloadend', tileLoadHandler);
        source.un('tileloaderror', errorHandler);
        console.log('[updateTileLayer] Cleaned up tile listeners');
      }
    };

    const tileLoadHandler = () => {
      console.log('[updateTileLayer] ✓✓✓ TILE LOAD END EVENT FIRED ✓✓✓');
      hideSpinner();
    };

    const errorHandler = () => {
      console.log('[updateTileLayer] ✗✗✗ TILE LOAD ERROR EVENT FIRED ✗✗✗');
      hideSpinner();
    };

    source.on('tileloadend', tileLoadHandler);
    source.on('tileloaderror', errorHandler);

    this.Map.addLayer(this.currentTileLayer);
    this.currentLayer = layer;
    this.currentProjection = projection;

    console.log(`[updateTileLayer] Layer added to map: ${layerKey}`);

    if (fitToBounds || this.shouldFitToBounds) {
      setTimeout(async () => {
        await this.fitToLayerBounds(validationIdValue, projection);
      }, 200);
    }
  }




  public reloadCurrentLayer() {
    if (!this.currentTileLayer || !this.currentLayer) {
      console.warn('No current tile layer to reload');
      return;
    }

    // Don't show spinner for refresh
    const source = this.currentTileLayer.getSource();
    if (source && typeof (source as any).refresh === 'function') {
      (source as any).refresh();
      console.log('Requested tile source refresh');
    } else {
      console.warn('Tile source has no refresh method; re-create layer');
      if (this.currentLayer) {
        // Preserve the key to prevent spinner on refresh
        const preservedKey = this.currentLayerKey;
        this.updateTileLayer(this.currentLayer, this.currentProjection);
        this.currentLayerKey = preservedKey;
      }
    }
  }




  private async fitToLayerBounds(validationId: string, layerProjection: 'EPSG:4326' | 'EPSG:3857' = 'EPSG:4326') {
    console.log(`[fitToLayerBounds] Fetching bounds for ${validationId} (${layerProjection})`);
    try {
      const response = await fetch(`/api/${validationId}/bounds/`);
      if (!response.ok) {
        console.warn('[fitToLayerBounds] Could not fetch bounds');
        return;
      }

      const data = await response.json();
      if (!data.extent) {
        console.warn('[fitToLayerBounds] No extent in response');
        return;
      }

      let extent = data.extent;
      const backendCRS = data.crs || 'EPSG:4326';
      const viewProj = this.Map.getView().getProjection().getCode();

      console.log(`[fitToLayerBounds] Backend CRS=${backendCRS}, View CRS=${viewProj}`);

      if (backendCRS !== viewProj) {
        extent = transformExtent(extent, backendCRS, viewProj);
        console.log('[fitToLayerBounds] Transformed extent to view CRS');
      }

      this.Map.renderSync();
      this.Map.getView().fit(extent, {
        padding: [200, 200, 200, 200],
        duration: 1000,
        maxZoom: 18
      });
      console.log('[fitToLayerBounds] Fit view completed');
    } catch (error) {
      console.error('[fitToLayerBounds] Error:', error);
    }
  }





  async resetMapView() {
    const validationIdValue = this.validationId();
    if (this.Map && this.currentLayer && validationIdValue) {
      this.shouldFitToBounds = true; // allow fit on next update
      await this.fitToLayerBounds(validationIdValue, this.currentProjection);
    } else if (this.Map) {
      this.Map.getView().animate({
        center: [0, 0],
        zoom: 1,
        duration: 1000
      });
    }
  }


  public async toggleProjection() {
    if (!this.currentLayer) {
      console.warn('[toggleProjection] No current layer to toggle');
      return;
    }
    const validationIdValue = this.validationId();
    const newProj = this.currentProjection === 'EPSG:4326' ? 'EPSG:3857' : 'EPSG:4326';
    console.log(`[toggleProjection] Switching from ${this.currentProjection} to ${newProj}`);

    // Toggle base layers
    this.baseLayer4326.setVisible(newProj === 'EPSG:4326');
    this.baseLayer3857.setVisible(newProj === 'EPSG:3857');

    // Change the map's view projection
    const currentView = this.Map.getView();
    const newView = new View({
      projection: newProj,
      center: currentView.getCenter(),
      zoom: currentView.getZoom(),
      minZoom: 0,
      maxZoom: 18
    });

    this.Map.setView(newView);
    console.log(`[toggleProjection] Map view changed to ${newProj}`);

    // Reload the content tile layer in the new projection
    // This will trigger spinner because it's a "new" layer (different projection)
    await this.updateTileLayer(this.currentLayer, newProj);
    await this.fitToLayerBounds(validationIdValue, newProj);
  }

  toggleFullscreen(): void {
    const mapElement = document.getElementById('imap');

    if (!document.fullscreenElement) {
      // Enter fullscreen
      if (mapElement?.requestFullscreen) {
        mapElement.requestFullscreen();
      } else if ((mapElement as any)?.webkitRequestFullscreen) {
        (mapElement as any).webkitRequestFullscreen();
      } else if ((mapElement as any)?.msRequestFullscreen) {
        (mapElement as any).msRequestFullscreen();
      }
    } else {
      // Exit fullscreen
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if ((document as any).webkitExitFullscreen) {
        (document as any).webkitExitFullscreen();
      } else if ((document as any).msExitFullscreen) {
        (document as any).msExitFullscreen();
      }
    }
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

    // Find the layer in cached metadata to get its colormap info
    let colormapInfo = null;
    if (this.cachedMetadata.layers) {
      const layer = this.cachedMetadata.layers.find((l: any) =>
        l.name === selectedLayer.name && l.metric === currentMetric
      );
      if (layer && layer.colormap) {
        colormapInfo = layer.colormap;
      }
    }

    // Lazy-load vmin/vmax
    this.plotService.getLayerRange(
      this.validationId(),
      currentMetric,
      selectedLayer.name
    ).subscribe({
      next: (rangeData) => {
        const completeColormap = {
          ...(colormapInfo || {}),
          ...rangeData,
          metric_name: currentMetric
        };

        const isCategorical = completeColormap.is_categorical === true;

        if (isCategorical) {
          console.log('Loading categorical layer, calling showLegend');
          this.showLegend(completeColormap, selectedLayer);
          console.log('After showLegend, colorbarData:', this.colorbarData);
        } else {
          this.showColorbar(completeColormap);
        }
      },
      error: (error) => {
        console.error('Error fetching layer range:', error);
        // Fallback to default visualization
        this.showColorbar({
          vmin: 0,
          vmax: 1,
          metric_name: currentMetric,
          is_categorical: false
        });
      }
    });
  }


  // Helper method to get available layers for current metric
  getAvailableLayersForCurrentMetric(): LayerDetail[] {
    if (!this.cachedMetadata || !this.selectedMetric) {
      console.log('No cached metadata or selected metric for layers');
      return [];
    }

    // Try layer_mapping first (if it exists)
    if (this.cachedMetadata.layer_mapping) {
      const layerNames = this.cachedMetadata.layer_mapping[this.selectedMetric.metric_query_name];
      if (Array.isArray(layerNames) && layerNames.length > 0) {
        return layerNames.map(layerName => ({
          name: layerName,
          metricName: this.selectedMetric.metric_query_name
        }));
      }
    }

    // Fallback: filter layers by metric
    if (this.cachedMetadata.layers && Array.isArray(this.cachedMetadata.layers)) {
      const metricLayers = this.cachedMetadata.layers.filter(layer =>
        layer.metric === this.selectedMetric.metric_query_name
      );

      if (metricLayers.length > 0) {
        return metricLayers.map(layer => ({
          name: layer.name,
          metricName: this.selectedMetric.metric_query_name,
          colormap: layer.colormap
        }));
      }
    }

    console.log(`No layers found for metric: ${this.selectedMetric.metric_query_name}`);
    return [];
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
  // Properties - add these new ones
  candidates: any[] = [];
  multipleFound: boolean = false;
  showCandidateSelection: boolean = false;

  // Keep all existing properties
  isISMNData: boolean = false;
  stationName: string | null = null;
  networkName: string | null = null;
  landcoverType: string | null = null;
  climateKG: string | null = null;
  frmClass: string | null = null;
  varName: string | null = null;
  pointLoc: string | null = null;
  pointErrorMessage: string | null = null;
  instrument: string | null = null;
  instrumentDepthFrom: number | null = null;
  instrumentDepthTo: number | null = null;

  onMapClick(event: MapBrowserEvent<any>) {
    if (!this.currentLayer) return;

    // Hide existing popover first (if open)
    this.pointPopupVisible = false;
    const coordinate = event.coordinate;
    const [x, y] = coordinate;
    const z = this.Map.getView().getZoom();

    const epsgCode = this.currentProjection.replace('EPSG:', '');
    const validationIdValue = this.validationId();

    if (!validationIdValue) return;

    // Reset all dialog state
    this.pointQueryLoading = true;
    this.selectedPointValue = null;
    this.selectedPointCoords = null;
    this.pointErrorMessage = null;

    // Reset candidate selection state
    this.candidates = [];
    this.multipleFound = false;
    this.showCandidateSelection = false;

    // Reset data type specific fields
    this.resetDataFields();

    console.log('Querying point at:', { x, y, projection: epsgCode });

    this.httpClient.get(
      `/api/${validationIdValue}/point/${this.currentLayer.metricName}/${this.currentLayer.name}`,
      {
        params: {
          x: x.toString(),
          y: y.toString(),
          z: z?.toString(),
          projection: epsgCode
        }
      }
    ).subscribe({
      next: (response: any) => {
        this.pointQueryLoading = false;

        if (response && response.candidates && response.candidates.length > 0) {
          this.candidates = response.candidates;
          this.multipleFound = response.multiple_found;
          this.isISMNData = response.is_ismn;

          if (this.multipleFound) {
            // Show selection UI
            this.showCandidateSelection = true;
            console.log('Multiple candidates found:', this.candidates.length);
          } else {
            // Single result - display directly
            this.selectCandidate(this.candidates[0]);
          }
        } else {
          this.selectedPointValue = null;
          this.pointErrorMessage = 'No data returned from query';
          console.warn('No data returned from point query');
        }
        this.pointPopupVisible = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.pointQueryLoading = false;
        this.selectedPointValue = null;
        this.candidates = [];
        this.multipleFound = false;
        this.showCandidateSelection = false;
        this.resetDataFields();

        if (err.error?.error) {
          this.pointErrorMessage = err.error.error;
        } else if (err.status === 404) {
          this.pointErrorMessage = 'No data available at this location';
        } else {
          this.pointErrorMessage = 'An error occurred while fetching data';
        }

        console.error('Error fetching point value:', err);
        this.pointPopupVisible = true;
        this.cdr.detectChanges();
      }
    });
  }

  selectCandidate(candidate: any): void {
    this.showCandidateSelection = false;

    this.selectedPointValue = candidate.value;
    this.selectedPointCoords = {
      lat: candidate.lat,
      lon: candidate.lon
    };

    if (this.isISMNData) {
      this.stationName = candidate.station || 'Unknown Station';
      this.networkName = candidate.network || 'Unknown Network';
      this.landcoverType = candidate.lc_2010 || null;
      this.climateKG = candidate.climate_KG || null;
      this.frmClass = candidate.frm_class || null;
      this.varName = this.currentLayer?.name || null;
      this.pointLoc = candidate.gpi || null;
      this.instrument = candidate.instrument || null;
      this.instrumentDepthFrom = candidate.instrument_depthfrom !== undefined
        ? parseFloat(candidate.instrument_depthfrom)
        : null;
      this.instrumentDepthTo = candidate.instrument_depthto !== undefined
        ? parseFloat(candidate.instrument_depthto)
        : null;

      console.log('ISMN station selected:', {
        gpi: candidate.gpi,
        station: this.stationName,
        network: this.networkName
      });
    } else {
      this.varName = this.currentLayer?.name || null;
      this.pointLoc = candidate.gpi?.toString() || null;


      console.log('Gridded point selected:', {
        gpi: candidate.gpi,
        value: this.selectedPointValue
      });
    }

    this.cdr.detectChanges();
  }

  getCandidateName(candidate: any): string {
    if (this.isISMNData) {
      const network = candidate.network || 'Unknown';
      const station = candidate.station || 'Unknown';
      const instrument = candidate.instrument;
      const depthFrom = candidate.instrument_depthfrom;
      const depthTo = candidate.instrument_depthto;

      let label = `${network} – ${station}`;

      if (instrument) {
        label += ` – ${instrument}`;
      }

      if (depthFrom !== undefined && depthTo !== undefined) {
        label += ` (${Number(depthFrom).toFixed(2)}–${Number(depthTo).toFixed(2)} m)`;
      } else if (depthFrom !== undefined) {
        label += ` (${Number(depthFrom).toFixed(2)} m)`;
      }

      return label;
    } else {
      const lat = Number(candidate.lat).toFixed(3);
      const lon = Number(candidate.lon).toFixed(3);
      return `Grid Point ${candidate.gpi}`;
    }
  }

  trackByGpi(index: number, candidate: any): number {
    return candidate.gpi;
  }

  getDialogHeader(): string {
    if (this.pointQueryLoading) {
      return 'Loading...';
    }
    if (this.showCandidateSelection) {
      return `Select Point (${this.candidates.length} found)`;
    }
    // ISMN: Station name as header
    if (this.isISMNData && this.selectedPointValue !== null) {
      return this.stationName || 'Station Data';
    }
    // Gridded: Use layer name or generic "Grid Point"
    if (this.selectedPointValue !== null) {
      return this.varName || 'Grid Point';
    }
    return 'Point Query';
  }

  // New: Subtitle for ISMN showing network + sensor
  getDialogSubtitle(): string | null {
    if (!this.isISMNData || this.selectedPointValue === null || this.showCandidateSelection) {
      return null;
    }

    let subtitle = this.networkName || '';

    if (this.instrument) {
      subtitle += ` · ${this.instrument}`;
      if (this.instrumentDepthFrom !== null && this.instrumentDepthTo !== null) {
        subtitle += ` (${this.instrumentDepthFrom.toFixed(1)}–${this.instrumentDepthTo.toFixed(1)} m)`;
      } else if (this.instrumentDepthFrom !== null) {
        subtitle += ` (${this.instrumentDepthFrom.toFixed(1)} m)`;
      }
    }

    return subtitle || null;
  }


  getDialogSubheader(): string {
    if (this.pointQueryLoading || this.showCandidateSelection) {
      return '';
    }

    // ISMN: Network + sensor info
    if (this.isISMNData && this.selectedPointValue !== null) {
      let subtitle = this.networkName || '';

      if (this.instrument) {
        subtitle += ` · ${this.instrument}`;

        if (this.instrumentDepthFrom !== null && this.instrumentDepthTo !== null) {
          subtitle += ` (${this.instrumentDepthFrom.toFixed(1)}–${this.instrumentDepthTo.toFixed(1)} m)`;
        } else if (this.instrumentDepthFrom !== null) {
          subtitle += ` (${this.instrumentDepthFrom.toFixed(1)} m)`;
        }
      }

      return subtitle;
    }

    // Gridded: Show "Gridded Data" as subtitle
    if (this.selectedPointValue !== null) {
      return 'Gridded Data';
    }

    return '';
  }

  private resetDataFields(): void {
    this.isISMNData = false;
    this.stationName = null;
    this.networkName = null;
    this.landcoverType = null;
    this.climateKG = null;
    this.frmClass = null;
    this.varName = null;
    this.pointLoc = null;
    this.instrument = null;
    this.instrumentDepthFrom = null;
    this.instrumentDepthTo = null;
  }


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
    this.currentLayerKey = '';
    this.isLoading = false;
    this.cdr.detectChanges(); // Force detection
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

    // Try to get status legend from cached metadata first
    let statusLegend = this.cachedMetadata?.status_metadata?.[selectedLayer.name];

    // If not in cache, build it from colorbarData
    if (!statusLegend && colorbarData.categories && colorbarData.colormap_info?.colors) {
      console.log('Building legend from colorbarData (not in cache)');
      statusLegend = this.buildStatusLegendFromColorbarData(colorbarData);
    }

    if (statusLegend && this.legendControl) {
      const legendData = {
        ...colorbarData,
        legend_data: statusLegend
      };

      this.legendControl.updateLegend(legendData, selectedLayer.metricName);

      // IMPORTANT: Store the complete legend data for snapshots
      this.colorbarData = legendData;

      console.log('Legend data stored for snapshot:', this.colorbarData);
    } else {
      console.warn('No status legend data found for layer:', selectedLayer.name);
      if (this.legendControl) {
        this.legendControl.updateLegend(null, '');
      }
      // Clear colorbarData if no legend
      this.colorbarData = null;
    }
  }

  private buildStatusLegendFromColorbarData(colorbarData: any): any {
    const legendEntries = Object.entries(colorbarData.categories)
      .sort(([keyA], [keyB]) => Number(keyA) - Number(keyB))
      .map(([statusCode, label]) => {
        const statusCodeInt = Number(statusCode);
        // Map status code to color index (shift by 1)
        const colorIndex = statusCodeInt + 1;

        const rgba = colorbarData.colormap_info.colors[colorIndex];
        const color = rgba
          ? `rgba(${Math.round(rgba[0] * 255)}, ${Math.round(rgba[1] * 255)}, ${Math.round(rgba[2] * 255)}, ${rgba[3] || 1})`
          : '#cccccc';

        return {
          value: statusCodeInt,
          label: `${label}`,
          color: color
        };
      });

    return {
      entries: legendEntries
    };
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
  @HostListener('document:keydown.escape')
  onEscapeKey() {
    if (this.pointPopupVisible) {
      this.pointPopupVisible = false;
      this.cdr.detectChanges();
    }
  }

  // Close dialog on click outside
  @HostListener('document:mousedown', ['$event'])
  onClickOutside(event: MouseEvent) {
    if (!this.pointPopupVisible) return;

    const target = event.target as HTMLElement;

    // Don't close if clicking inside the dialog
    const dialogElement = document.querySelector('.p-dialog');
    if (dialogElement && dialogElement.contains(target)) {
      return;
    }

    this.pointPopupVisible = false;
    this.cdr.detectChanges();
  }
}


export class AngularControl extends Control {
  constructor(angularElement: HTMLElement) {
    // Add OpenLayers classes directly to the Angular element
    angularElement.classList.add('ol-unselectable', 'ol-control');

    super({
      element: angularElement
    });
  }
}

export interface LayerDetail {
  name: string;           // Variable name (var_name) for backend requests
  metricName: string;     // Metric this layer belongs to
  colormap?: any;         // Colormap metadata from backend (optional)
}



export interface ValidationMetadata {
  validation_id: string;
  layer_mapping: { [metric: string]: string[] };
}


