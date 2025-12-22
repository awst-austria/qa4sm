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
import { transformExtent } from 'ol/proj';
import { FullScreen, Control } from 'ol/control';
import { SharedPrimeNgModule } from '../../../../shared.primeNg.module';
import { WebsiteGraphicsService } from '../../../core/services/global/website-graphics.service';
import { TiffLayer } from './interfaces/layer.interfaces';
import { ValidationrunDto } from '../../../core/services/validation-run/validationrun.dto';
import { MetricsPlotsDto } from '../../../core/services/validation-run/metrics-plots.dto';
import { LegendControl } from './control/legend-control';
import { OpacitySliderControl } from './control/opacity-slider.control';
import { ValidationrunService } from '../../../core/services/validation-run/validationrun.service';
import { Popover } from 'primeng/popover';

// Constants
const EPSG_4326 = 'EPSG:4326';
const EPSG_3857 = 'EPSG:3857';
const DEFAULT_OPACITY = 0.7;
const DEFAULT_ZOOM = 2;
const MIN_ZOOM = 0;
const MAX_ZOOM = 15;
const DEFAULT_TILE_SIZE = 256;
const BASE_URL_EOX = 'https://tiles.maps.eox.at/wms';
const BASE_URL_OSM = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
const DEFAULT_SNAPSHOT_TITLE = 'Snapshot';
const DEFAULT_COLORBAR_GRADIENT = 'linear-gradient(to right, blue, cyan, yellow, red)';
const CANVAS_PADDING = 40;
const COLORBAR_HEIGHT = 20;
const COLORBAR_BORDER_RADIUS = 4;
const LEGEND_PADDING = 20;
const LEGEND_ITEM_HEIGHT = 24;
const LEGEND_SYMBOL_SIZE = 16;
const LEGEND_GAP = 8;
const LEGEND_TITLE_HEIGHT = 30;
const LEGEND_SEPARATOR_GAP = 8;
const TILE_GRID_MAX_ZOOM = 18;
const WEB_MERCATOR_EXTENT_MAX = 20037508.342789244;
const WEB_MERCATOR_INITIAL_RESOLUTION = 156543.03392804097;
const MAP_FIT_PADDING = 200;

type Projection = 'EPSG:4326' | 'EPSG:3857';

@Component({
  selector: 'qa-interactive-map',
  standalone: true,
  imports: [MapModule, SharedPrimeNgModule, Popover],
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
  private cdr = inject(ChangeDetectorRef);

  validationId = input('');
  @Input() validationRun: ValidationrunDto;

  Map: Map;
  clusteredSource: VectorSource = new VectorSource();
  availableLayers: TiffLayer[] = [];
  currentLayer: TiffLayer | null = null;
  currentTileLayer: any = null;
  isLoading = false;
  private currentLayerKey = '';
  cachedMetadata: any = null;
  selectedLayerForMetric: { [metric: string]: LayerDetail } = {};
  colorbarData: any = null;
  private legendControl: LegendControl | null = null;
  statusMetadata: any = null;
  selectedMetric: MetricsPlotsDto = {} as MetricsPlotsDto;
  metrics: MetricsPlotsDto[] = [];
  public currentProjection: Projection = 'EPSG:4326';
  private baseLayer4326!: TileLayer<TileWMS>;
  private baseLayer3857!: TileLayer<XYZ>;
  private shouldFitToBounds = true;
  private completeColormap: any = null;
  showSnapshotModal = false;
  snapshotImageSrc: string | null = null;
  isFullscreen = false;
  pointPopupVisible = false;
  snapshotTitle = DEFAULT_SNAPSHOT_TITLE;
  private opacityControl!: OpacitySliderControl;

  // Point query state
  selectedPointValue: string | null = null;
  selectedPointCoords: { lat: number; lon: number } | null = null;
  pointQueryLoading = false;
  pointErrorMessage: string | null = null;
  candidates: any[] = [];
  multipleFound = false;
  showCandidateSelection = false;
  isISMNData = false;
  stationName: string | null = null;
  networkName: string | null = null;
  landcoverType: string | null = null;
  climateKG: string | null = null;
  frmClass: string | null = null;
  varName: string | null = null;
  pointLoc: string | null = null;
  instrument: string | null = null;
  instrumentDepthFrom: number | null = null;
  instrumentDepthTo: number | null = null;

  private fullscreenHandler = () => {
    this.isFullscreen = document.fullscreenElement !== null;
    this.cdr.detectChanges();
  };

  constructor(
    public plotService: WebsiteGraphicsService,
    private validationRunService: ValidationrunService
  ) { }

  ngAfterViewInit() {
    this.initMap();
    this.loadInitialMetric();
    this.addAngularControlsToMap();
    document.addEventListener('fullscreenchange', this.fullscreenHandler);
  }

  ngOnDestroy() {
    this.Map?.dispose();
    document.removeEventListener('fullscreenchange', this.fullscreenHandler);
  }

  // Helper to update loading state and trigger change detection
  private setLoading(loading: boolean): void {
    this.isLoading = loading;
    this.cdr.detectChanges();
  }

  private setupMapClickHandler() {
    this.Map.on('singleclick', (event: MapBrowserEvent<any>) => this.onMapClick(event));
  }

  private loadMetadataAndInitializeLayers() {
    const zarrMetrics = this.selectedMetric.zarr_metrics || {};

    this.plotService.getValidationMetadata(this.validationId(), zarrMetrics).subscribe({
      next: (metadata) => {
        console.log('Received metadata:', metadata);
        this.cachedMetadata = metadata;
        this.statusMetadata = metadata.status_metadata || {};

        if (!metadata.layers?.length) {
          console.error('No layers found in metadata');
          this.setLoading(false);
          return;
        }

        metadata.layers.forEach((layer: any) => {
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
            this.setLoading(false);
            this.addTileLayerForMetric();
          } else {
            this.clearMapAndLegend();
          }
        } else {
          this.setLoading(false);
        }
      },
      error: (error) => {
        console.error('Error loading metadata:', error);
        this.setLoading(false);
      }
    });
  }

  onLayerSelectionChange(metric: string, selectedLayer: LayerDetail | null) {
    if (!selectedLayer) {
      console.warn('No layer found for selection');
      return;
    }

    this.selectedLayerForMetric[metric] = selectedLayer;

    if (this.selectedMetric?.metric_query_name === metric) {
      this.addTileLayerForMetric();
    }
  }

  onMetricChange(event: any): void {
    this.shouldFitToBounds = false;
    this.selectedMetric = event.value;

    if (this.cachedMetadata) {
      if (this.selectedLayerForMetric[this.selectedMetric.metric_query_name]) {
        this.addTileLayerForMetric();
      } else {
        this.clearMapAndLegend();
      }
    } else {
      this.isLoading = true;
      this.loadMetadataAndInitializeLayers();
    }
  }

  private initMap() {
    this.baseLayer4326 = new TileLayer({
      source: new TileWMS({
        url: BASE_URL_EOX,
        params: { LAYERS: 'terrain-light', TILED: true, CRS: EPSG_4326 },
        serverType: 'geoserver',
        attributions: 'Data © OpenStreetMap contributors and others, Rendering © EOX',
        crossOrigin: 'anonymous'
      }),
      visible: true
    });

    this.baseLayer3857 = new TileLayer({
      source: new XYZ({
        url: BASE_URL_OSM,
        attributions: '© OpenStreetMap contributors',
        crossOrigin: 'anonymous'
      }),
      visible: false
    });

    this.opacityControl = new OpacitySliderControl({
      initialOpacity: DEFAULT_OPACITY
    });

    this.Map = new Map({
      target: 'imap',
      layers: [this.baseLayer4326, this.baseLayer3857],
      view: new View({
        projection: EPSG_4326,
        center: [0, 0],
        zoom: DEFAULT_ZOOM,
        minZoom: MIN_ZOOM,
        maxZoom: MAX_ZOOM
      }),
      controls: [new FullScreen(), this.opacityControl]
    });

    this.legendControl = new LegendControl({ colorbarData: null, metricName: '' });
    this.Map.addControl(this.legendControl);
    this.setupMapClickHandler();
  }

  private addAngularControlsToMap(): void {
    if (!this.Map) {
      console.error('Map not initialized');
      return;
    }

    const containers = [
      this.metricDropdownContainer,
      this.layerDropdownContainer,
      this.snapshotButtonContainer,
      this.projectionToggleContainer
    ];

    containers.forEach(container => {
      const element = container.nativeElement;
      element.style.display = 'block';
      this.Map.addControl(new AngularControl(element));
    });
  }

  takeSnapshot(): void {
    if (!this.Map) {
      console.error('Map not initialized');
      return;
    }

    const captureMap = () => {
      try {
        const mapCanvas = document.createElement('canvas');
        const size = this.Map!.getSize();
        if (!size) return;

        mapCanvas.width = size[0];
        mapCanvas.height = size[1];
        const mapContext = mapCanvas.getContext('2d');
        if (!mapContext) return;

        const canvases = document.querySelectorAll('#imap .ol-layer canvas');
        canvases.forEach((canvas: HTMLCanvasElement) => {
          if (canvas.width > 0) {
            const opacity = (canvas.parentNode as HTMLElement).style.opacity;
            mapContext.globalAlpha = opacity === '' ? 1 : Number(opacity);
            const matrix = canvas.style.transform.match(/^matrix\(([^\(]*)\)$/);
            if (matrix) {
              mapContext.setTransform(...matrix[1].split(',').map(Number) as [number, number, number, number, number, number]);
            }
            mapContext.drawImage(canvas, 0, 0);
          }
        });

        mapContext.globalAlpha = 1;
        mapContext.setTransform(1, 0, 0, 1, 0, 0);

        if (this.colorbarData) {
          if (this.colorbarData.is_categorical) {
            this.drawLegendOnCanvas(mapContext, mapCanvas);
          } else {
            this.drawColorbarOnCanvas(mapContext, mapCanvas);
          }
        }
        this.snapshotImageSrc = mapCanvas.toDataURL('image/png');
        this.snapshotTitle = this.currentLayerKey?.replace(/:/g, '')
          || this.selectedMetric?.metric_pretty_name
          || DEFAULT_SNAPSHOT_TITLE;
        this.showSnapshotModal = true;
        this.cdr.detectChanges();
      } catch (error) {
        console.error('Error capturing snapshot:', error);
        alert('Unable to capture snapshot. The map may contain protected content.');
      }
    };

    if (this.isFullscreen) {
      document.exitFullscreen()
        .then(() => setTimeout(captureMap, 300))
        .catch(() => captureMap());
    } else {
      captureMap();
    }
  }

  private drawLegendOnCanvas(ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement): void {
    const entries = this.colorbarData?.legend_data?.entries;
    if (!entries) return;

    const padding = LEGEND_PADDING;
    const maxLabelWidth = 180;
    const legendWidth = LEGEND_SYMBOL_SIZE + LEGEND_GAP + maxLabelWidth + padding * 2;
    const legendHeight = LEGEND_TITLE_HEIGHT + LEGEND_SEPARATOR_GAP + (entries.length * LEGEND_ITEM_HEIGHT) + padding;
    const x = canvas.width - legendWidth - LEGEND_PADDING;
    const y = canvas.height - legendHeight - LEGEND_PADDING;

    // Background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.fillRect(x, y, legendWidth, legendHeight);
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.15)';
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, legendWidth, legendHeight);

    // Title
    ctx.fillStyle = '#2c3e50';
    ctx.font = 'bold 13px Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(this.colorbarData.metric_name || 'Status', x + legendWidth / 2, y + padding + 10);

    // Separator
    const separatorY = y + padding + 18;
    ctx.strokeStyle = '#e0e0e0';
    ctx.beginPath();
    ctx.moveTo(x + padding, separatorY);
    ctx.lineTo(x + legendWidth - padding, separatorY);
    ctx.stroke();

    // Legend items
    ctx.font = '11px Arial, sans-serif';
    ctx.textAlign = 'left';

    entries.forEach((entry: any, index: number) => {
      const itemY = separatorY + LEGEND_SEPARATOR_GAP + (index * LEGEND_ITEM_HEIGHT);

      ctx.fillStyle = entry.color;
      ctx.fillRect(x + padding, itemY, LEGEND_SYMBOL_SIZE, LEGEND_SYMBOL_SIZE);

      ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
      ctx.strokeRect(x + padding, itemY, LEGEND_SYMBOL_SIZE, LEGEND_SYMBOL_SIZE);

      ctx.fillStyle = '#34495e';
      ctx.fillText(entry.label, x + padding + LEGEND_SYMBOL_SIZE + LEGEND_GAP, itemY + LEGEND_SYMBOL_SIZE / 2 + 4);
    });
  }

  private drawColorbarOnCanvas(ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement): void {
    const barWidth = Math.max(500, canvas.width - CANVAS_PADDING * 2);
    const x = (canvas.width - barWidth) / 2;
    const y = canvas.height - 60;

    // Background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.fillRect(0, canvas.height - 70, canvas.width, 70);

    // Gradient bar
    const gradient = ctx.createLinearGradient(x, y, x + barWidth, y);
    const colors = this.parseGradientColors(this.colorbarData.gradient);
    colors.forEach((color, index) => gradient.addColorStop(index / (colors.length - 1), color));

    ctx.beginPath();
    ctx.roundRect(x, y, barWidth, COLORBAR_HEIGHT, COLORBAR_BORDER_RADIUS);
    ctx.fillStyle = gradient;
    ctx.fill();
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.stroke();

    // Labels
    ctx.fillStyle = '#2c3e50';
    ctx.font = '12px Arial, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(parseFloat(this.completeColormap.vmin.toFixed(3)).toString(), x, y + COLORBAR_HEIGHT + 15);
    console.log(' should be vmin !!! : ' + this.completeColormap.vmin.toFixed(3).toString())
    ctx.textAlign = 'center';
    ctx.font = 'bold 13px Arial, sans-serif';
    ctx.fillText(this.colorbarData.metric_name, canvas.width / 2, y + COLORBAR_HEIGHT + 15);

    ctx.textAlign = 'right';
    ctx.font = '12px Arial, sans-serif';
    ctx.fillText(parseFloat(this.completeColormap.vmax.toFixed(3)).toString(), x + barWidth, y + COLORBAR_HEIGHT + 15);
    console.log(' should be vmax !!! : ' + this.completeColormap.vmax.toFixed(3).toString())
  }

  private parseGradientColors(gradientString: string): string[] {
    const matches = gradientString.match(/#[0-9a-f]{6}|rgb\([^)]+\)|rgba\([^)]+\)/gi);
    return matches || ['#ffffff', '#000000'];
  }

  downloadSnapshot(): void {
    if (!this.snapshotImageSrc) return;
    const link = document.createElement('a');
    link.download = `${this.snapshotTitle.replace(/[^a-z0-9]/gi, '-').toLowerCase() || 'map-snapshot'}.png`;
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
    if (!validationIdValue || !this.selectedMetric || !this.cachedMetadata) {
      console.error('Missing required data for tile layer');
      return;
    }

    const currentMetric = this.selectedMetric.metric_query_name;
    const selectedLayer = this.selectedLayerForMetric[currentMetric];

    if (!selectedLayer) {
      console.error(`No layer selected for metric: ${currentMetric}`);
      return;
    }

    const metricLayer: TiffLayer = {
      name: selectedLayer.name || this.selectedMetric.metric_pretty_name || 'Metric Layer',
      metricName: selectedLayer.metricName,
      opacity: DEFAULT_OPACITY,
      isLoaded: false
    };

    this.updateTileLayer(metricLayer, this.currentProjection);
    this.updateVisualizationForCurrentMetric();
  }

  isCurrentMetricStatus(): boolean {
    return this.selectedMetric?.metric_query_name === 'status';
  }

  getStatusLegendEntries(): any[] {
    return this.colorbarData?.legend_data?.entries || [];
  }

  private createTileGridForProjection(projection: Projection) {
    if (projection === 'EPSG:4326') {
      const resolutions = Array.from({ length: TILE_GRID_MAX_ZOOM + 1 }, (_, z) =>
        180 / (DEFAULT_TILE_SIZE * Math.pow(2, z))
      );
      return new TileGrid({
        extent: [-180, -90, 180, 90],
        origin: [-180, 90],
        resolutions,
        tileSize: DEFAULT_TILE_SIZE
      });
    } else {
      const extent = [-WEB_MERCATOR_EXTENT_MAX, -WEB_MERCATOR_EXTENT_MAX, WEB_MERCATOR_EXTENT_MAX, WEB_MERCATOR_EXTENT_MAX];
      const resolutions = Array.from({ length: TILE_GRID_MAX_ZOOM + 1 }, (_, z) =>
        WEB_MERCATOR_INITIAL_RESOLUTION / Math.pow(2, z)
      );
      return new TileGrid({
        extent,
        origin: [extent[0], extent[3]],
        resolutions,
        tileSize: DEFAULT_TILE_SIZE
      });
    }
  }

  private async updateTileLayer(layer: TiffLayer, projection: Projection = 'EPSG:4326', fitToBounds = false) {
    const layerKey = `${layer.name}_${projection}`;
    const isNewLayer = this.currentLayerKey !== layerKey;

    if (isNewLayer) {
      this.currentLayerKey = layerKey;
      this.isLoading = true;
    }

    if (this.currentTileLayer) {
      this.Map.removeLayer(this.currentTileLayer);
    }

    const validationIdValue = this.validationId();
    if (!validationIdValue) {
      this.setLoading(false);
      return;
    }

    const epsgCode = projection.replace('EPSG:', '');
    const tileUrl = `/api/${validationIdValue}/tiles/${layer.metricName}/${layer.name}/${epsgCode}/{z}/{x}/{y}.png`;

    this.currentTileLayer = new TileLayer({
      source: new XYZ({
        url: tileUrl,
        tileSize: DEFAULT_TILE_SIZE,
        projection,
        tileGrid: this.createTileGridForProjection(projection)
      }),
      opacity: this.opacityControl.getSliderValue()
    });
    this.opacityControl.setLayer(this.currentTileLayer);

    const source = this.currentTileLayer.getSource();
    let firstTileReceived = false;

    const hideSpinner = () => {
      if (!firstTileReceived && this.isLoading) {
        firstTileReceived = true;
        this.setLoading(false);
        source.un('tileloadend', hideSpinner);
        source.un('tileloaderror', hideSpinner);
      }
    };

    source.on('tileloadend', hideSpinner);
    source.on('tileloaderror', hideSpinner);

    this.Map.addLayer(this.currentTileLayer);
    this.currentLayer = layer;
    this.currentProjection = projection;

    if (fitToBounds || this.shouldFitToBounds) {
      setTimeout(() => this.fitToLayerBounds(validationIdValue, projection), 200);
    }
  }

  public reloadCurrentLayer() {
    if (!this.currentTileLayer || !this.currentLayer) return;

    const source = this.currentTileLayer.getSource();
    if (typeof source?.refresh === 'function') {
      source.refresh();
    } else if (this.currentLayer) {
      const preservedKey = this.currentLayerKey;
      this.updateTileLayer(this.currentLayer, this.currentProjection);
      this.currentLayerKey = preservedKey;
    }
  }

  private async fitToLayerBounds(validationId: string, layerProjection: Projection = 'EPSG:4326') {
    try {
      const response = await fetch(`/api/${validationId}/bounds/`);
      if (!response.ok) return;

      const data = await response.json();
      if (!data.extent) return;

      let extent = data.extent;
      const backendCRS = data.crs || 'EPSG:4326';
      const viewProj = this.Map.getView().getProjection().getCode();

      if (backendCRS !== viewProj) {
        extent = transformExtent(extent, backendCRS, viewProj);
      }

      this.Map.renderSync();
      this.Map.getView().fit(extent, {
        padding: [MAP_FIT_PADDING, MAP_FIT_PADDING, MAP_FIT_PADDING, MAP_FIT_PADDING],
        duration: 1000,
        maxZoom: MAX_ZOOM
      });
    } catch (error) {
      console.error('[fitToLayerBounds] Error:', error);
    }
  }

  async resetMapView() {
    const validationIdValue = this.validationId();
    if (this.Map && this.currentLayer && validationIdValue) {
      this.shouldFitToBounds = true;
      await this.fitToLayerBounds(validationIdValue, this.currentProjection);
    } else if (this.Map) {
      this.Map.getView().animate({ center: [0, 0], zoom: 1, duration: 1000 });
    }
  }

  public async toggleProjection() {
    if (!this.currentLayer) return;

    const validationIdValue = this.validationId();
    const newProj: Projection = this.currentProjection === 'EPSG:4326' ? 'EPSG:3857' : 'EPSG:4326';

    this.baseLayer4326.setVisible(newProj === 'EPSG:4326');
    this.baseLayer3857.setVisible(newProj === 'EPSG:3857');

    const currentView = this.Map.getView();
    this.Map.setView(new View({
      projection: newProj,
      center: currentView.getCenter(),
      zoom: currentView.getZoom(),
      minZoom: MIN_ZOOM,
      maxZoom: TILE_GRID_MAX_ZOOM
    }));

    await this.updateTileLayer(this.currentLayer, newProj);
    await this.fitToLayerBounds(validationIdValue, newProj);
  }

  toggleFullscreen(): void {
    const mapElement = document.getElementById('imap') as any;
    if (!document.fullscreenElement) {
      (mapElement?.requestFullscreen || mapElement?.webkitRequestFullscreen || mapElement?.msRequestFullscreen)?.call(mapElement);
    } else {
      (document.exitFullscreen || (document as any).webkitExitFullscreen || (document as any).msExitFullscreen)?.call(document);
    }
  }

  private updateVisualizationForCurrentMetric() {
    if (!this.selectedMetric || !this.cachedMetadata) {
      this.clearMapAndLegend();
      return;
    }

    const currentMetric = this.selectedMetric.metric_query_name;
    const selectedLayer = this.selectedLayerForMetric[currentMetric];

    if (!selectedLayer) {
      this.clearMapAndLegend();
      return;
    }

    const colormapInfo = this.cachedMetadata.layers?.find((l: any) =>
      l.name === selectedLayer.name && l.metric === currentMetric
    )?.colormap || null;

    this.plotService.getLayerRange(this.validationId(), currentMetric, selectedLayer.name).subscribe({
      next: (rangeData) => {
        this.completeColormap = { ...colormapInfo, ...rangeData, metric_name: currentMetric };
        if (this.completeColormap.is_categorical) {
          this.showLegend(this.completeColormap, selectedLayer);
        } else {
          this.showColorbar(this.completeColormap);
        }
      },
      error: () => {
        this.showColorbar({ vmin: 0, vmax: 1, metric_name: currentMetric, is_categorical: false });
      }
    });
  }

  getAvailableLayersForCurrentMetric(): LayerDetail[] {
    if (!this.cachedMetadata || !this.selectedMetric) return [];

    const metricName = this.selectedMetric.metric_query_name;

    if (this.cachedMetadata.layer_mapping?.[metricName]?.length) {
      return this.cachedMetadata.layer_mapping[metricName].map((name: string) => ({
        name,
        metricName
      }));
    }

    return (this.cachedMetadata.layers || [])
      .filter((layer: any) => layer.metric === metricName)
      .map((layer: any) => ({
        name: layer.name,
        metricName,
        colormap: layer.colormap
      }));
  }

  currentMetricHasMultipleLayers(): boolean {
    const metricData = this.cachedMetadata?.layer_mapping?.[this.selectedMetric?.metric_query_name];
    return metricData ? Object.keys(metricData).length > 1 : false;
  }

  getLayerByName(layerName: string): LayerDetail | null {
    return this.getAvailableLayersForCurrentMetric().find(l => l.name === layerName) || null;
  }

  getColorbarData(metricName: string, index: number): Observable<any> {
    return this.httpClient.get(`/api/${this.validationId()}/colorbar/${metricName}/${index}/`);
  }

  getColorbarGradient(): string {
    return this.colorbarData?.gradient || DEFAULT_COLORBAR_GRADIENT;
  }

  getColorbarMin(): string {
    return this.completeColormap?.vmin?.toFixed(2) || '0.0';
  }

  getColorbarMax(): string {
    return this.completeColormap?.vmax?.toFixed(2) || '1.0';
  }

  onMapClick(event: MapBrowserEvent<any>) {
    if (!this.currentLayer) return;

    this.pointPopupVisible = false;
    const [x, y] = event.coordinate;
    const z = this.Map.getView().getZoom();
    const validationIdValue = this.validationId();
    if (!validationIdValue) return;

    this.resetPointQueryState();
    this.pointQueryLoading = true;

    this.httpClient.get(
      `/api/${validationIdValue}/point/${this.currentLayer.metricName}/${this.currentLayer.name}`,
      { params: { x: x.toString(), y: y.toString(), z: z?.toString(), projection: this.currentProjection.replace('EPSG:', '') } }
    ).subscribe({
      next: (response: any) => {
        this.pointQueryLoading = false;

        if (response?.candidates?.length) {
          this.candidates = response.candidates;
          this.multipleFound = response.multiple_found;
          this.isISMNData = response.is_ismn;

          if (this.multipleFound) {
            this.showCandidateSelection = true;
          } else {
            this.selectCandidate(this.candidates[0]);
          }
        } else {
          this.pointErrorMessage = 'No data returned from query';
        }
        this.pointPopupVisible = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.pointQueryLoading = false;
        this.pointErrorMessage = err.error?.error || (err.status === 404 ? 'No data available at this location' : 'An error occurred while fetching data');
        this.pointPopupVisible = true;
        this.cdr.detectChanges();
      }
    });
  }

  private resetPointQueryState(): void {
    this.selectedPointValue = null;
    this.selectedPointCoords = null;
    this.pointErrorMessage = null;
    this.candidates = [];
    this.multipleFound = false;
    this.showCandidateSelection = false;
    this.resetDataFields();
  }

  selectCandidate(candidate: any): void {
    this.showCandidateSelection = false;
    this.selectedPointValue = candidate.value;
    this.selectedPointCoords = { lat: candidate.lat, lon: candidate.lon };

    if (this.isISMNData) {
      this.stationName = candidate.station || 'Unknown Station';
      this.networkName = candidate.network || 'Unknown Network';
      this.landcoverType = candidate.lc_2010 || null;
      this.climateKG = candidate.climate_KG || null;
      this.frmClass = candidate.frm_class || null;
      this.varName = this.currentLayer?.name || null;
      this.pointLoc = candidate.gpi || null;
      this.instrument = candidate.instrument || null;
      this.instrumentDepthFrom = candidate.instrument_depthfrom != null ? parseFloat(candidate.instrument_depthfrom) : null;
      this.instrumentDepthTo = candidate.instrument_depthto != null ? parseFloat(candidate.instrument_depthto) : null;
    } else {
      this.varName = this.currentLayer?.name || null;
      this.pointLoc = candidate.gpi?.toString() || null;
    }

    this.cdr.detectChanges();
  }

  getCandidateName(candidate: any): string {
    if (this.isISMNData) {
      let label = `${candidate.network || 'Unknown'} – ${candidate.station || 'Unknown'}`;
      if (candidate.instrument) label += ` – ${candidate.instrument}`;
      if (candidate.instrument_depthfrom != null && candidate.instrument_depthto != null) {
        label += ` (${Number(candidate.instrument_depthfrom).toFixed(2)}–${Number(candidate.instrument_depthto).toFixed(2)} m)`;
      } else if (candidate.instrument_depthfrom != null) {
        label += ` (${Number(candidate.instrument_depthfrom).toFixed(2)} m)`;
      }
      return label;
    }
    return `Grid Point ${candidate.gpi}`;
  }

  trackByGpi(index: number, candidate: any): number {
    return candidate.gpi;
  }

  getDialogHeader(): string {
    if (this.pointQueryLoading) return 'Loading...';
    if (this.showCandidateSelection) return `Select Point (${this.candidates.length} found)`;
    if (this.isISMNData && this.selectedPointValue !== null) return this.stationName || 'Station Data';
    if (this.selectedPointValue !== null) return this.varName || 'Grid Point';
    return 'Point Query';
  }

  getDialogSubheader(): string {
    if (this.pointQueryLoading || this.showCandidateSelection) return '';

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

    return this.selectedPointValue !== null ? 'Gridded Data' : '';
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
    this.legendControl?.updateLegend(null, '');
    this.colorbarData = null;
    this.currentLayerKey = '';
    this.setLoading(false);
  }

  private showColorbar(colorbarData: any) {
    this.legendControl?.updateLegend(null, '');
    this.colorbarData = colorbarData;
  }

  private showLegend(colorbarData: any, selectedLayer: LayerDetail) {
    let statusLegend = this.cachedMetadata?.status_metadata?.[selectedLayer.name];

    if (!statusLegend && colorbarData.categories && colorbarData.colormap_info?.colors) {
      statusLegend = this.buildStatusLegendFromColorbarData(colorbarData);
    }

    if (statusLegend && this.legendControl) {
      const legendData = { ...colorbarData, legend_data: statusLegend };
      this.legendControl.updateLegend(legendData, selectedLayer.metricName);
      this.colorbarData = legendData;
    } else {
      this.legendControl?.updateLegend(null, '');
      this.colorbarData = null;
    }
  }

  private buildStatusLegendFromColorbarData(colorbarData: any): any {
    const entries = Object.entries(colorbarData.categories)
      .sort(([a], [b]) => Number(a) - Number(b))
      .map(([statusCode, label]) => {
        const colorIndex = Number(statusCode) + 1;
        const rgba = colorbarData.colormap_info.colors[colorIndex];
        const color = rgba
          ? `rgba(${Math.round(rgba[0] * 255)}, ${Math.round(rgba[1] * 255)}, ${Math.round(rgba[2] * 255)}, ${rgba[3] || 1})`
          : '#cccccc';
        return { value: Number(statusCode), label: `${label}`, color };
      });

    return { entries };
  }

  private loadInitialMetric(): void {
    const params = new HttpParams().set('validationId', this.validationId());
    this.validationRunService.getMetricsAndPlotsNames(params).subscribe({
      next: (metrics) => {
        this.metrics = metrics;
        if (metrics.length > 0) {
          this.selectedMetric = metrics[0];
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

  @HostListener('document:mousedown', ['$event'])
  onClickOutside(event: MouseEvent) {
    if (!this.pointPopupVisible) return;
    const dialogElement = document.querySelector('.p-dialog');
    if (dialogElement?.contains(event.target as HTMLElement)) return;
    this.pointPopupVisible = false;
    this.cdr.detectChanges();
  }

}

export class AngularControl extends Control {
  constructor(angularElement: HTMLElement) {
    angularElement.classList.add('ol-unselectable', 'ol-control');
    super({ element: angularElement });
  }
}

export interface LayerDetail {
  name: string;
  metricName: string;
  colormap?: any;
}

export interface ValidationMetadata {
  validation_id: string;
  layer_mapping: { [metric: string]: string[] };
}
