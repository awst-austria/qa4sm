import {AfterViewInit, Component, ElementRef, EventEmitter, Input, NgZone, OnInit, Output} from '@angular/core';
import {Map, Overlay, View} from 'ol';
import {Coordinate} from 'ol/coordinate';
import {Attribution} from 'ol/control';
import Projection from 'ol/proj/Projection';
import {get as GetProjection, transform} from 'ol/proj';
import {Extent} from 'ol/extent';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';

import {BoundingBoxControl} from './bounding-box-control';
import {SpatialSubsetModel} from '../../../spatial-subset/components/spatial-subset/spatial-subset-model';
import {ToastService} from '../../../core/services/toast/toast.service';
import VectorSource from "ol/source/Vector";
import {GeoJSON} from "ol/format";
import VectorLayer from "ol/layer/Vector";
import {Circle, Fill, Stroke, Style} from "ol/style";
import {addCommon as addCommonProjections} from 'ol/proj.js';
import {Cluster} from "ol/source";
import {LegendItem} from '../legend-item';

@Component({
    selector: 'qa-map',
    templateUrl: './map.component.html',
    styleUrls: ['./map.component.scss'],
    standalone: false
})
export class MapComponent implements AfterViewInit, OnInit {

  @Input() center: Coordinate;
  @Input() zoom: number;
  @Input() spatialSubset: SpatialSubsetModel;
  view: View;
  projection: Projection;
  extent: Extent = [-20026376.39, -20048966.10,
    20026376.39, 20048966.10];
  Map: Map;
  clusteredSource: VectorSource = new VectorSource();
  nonClusteredSource: VectorSource = new VectorSource();
  @Output() mapReady = new EventEmitter<Map>();
  @Output() noIsmnPoints = new EventEmitter<boolean>(false);

  singleSensorMarkerRadius = 5;

  multipleSensorMarkerRadius = 6;
  multipleSensorStrokeColor = '#FFAC04';
  multipleSensorStrokeWidth = 4;

  singleLocationMarkerRadius = 5;
  singleLocationStrokeColor = '#005D00';
  singleLocationStrokeWidth = 3;

  legendItems: LegendItem[];

  propertyNames = {
    station: 'station',
    network: 'network',
    depthFrom: 'depth_from',
    depthTo: 'depth_to',
    timeRangeFrom: 'timerange_from',
    timeRangeTo: 'timerange_to',
    frmClass: 'frm_class'
  };

  constructor(private zone: NgZone,
              private toastService: ToastService,
              private elementRef: ElementRef) {
  }

  ngOnInit() {
    this.legendItems = [
      {
        label: "Multiple stations",
        tooltip: 'Zoom in to get more exact station locations. ',
        strokeColor: this.multipleSensorStrokeColor,
        radius: this.multipleSensorMarkerRadius,
        strokeWidth: this.multipleSensorStrokeWidth,
      },
      {
        label: "Single station",
        tooltip: 'There are multiple sensors at the location. Click on it to get more details',
        strokeColor: this.singleLocationStrokeColor,
        radius: this.singleLocationMarkerRadius,
        strokeWidth: this.singleLocationStrokeWidth,
      },
      {
        label: 'Single Sensor',
        tooltip: 'Station with a single sensor. Click on a point to find out more about the sensor.',
        strokeWidth: 0,
        fillColor: this.singleLocationStrokeColor,
        strokeColor: this.singleLocationStrokeColor,
        radius: this.singleSensorMarkerRadius
      },
    ];
  }

  public clearSelection() {
    this.clusteredSource.clear();
    this.nonClusteredSource.clear();
  }

  public addGeoJson(geoJson: string) {
    let features = new GeoJSON().readFeatures(geoJson, {
      dataProjection: 'EPSG:4326',
      featureProjection: 'EPSG:3857'
    });

    if (features.length > 0){
      features[0].getGeometry().getType() === 'Polygon' ? this.nonClusteredSource.addFeatures(features) : this.clusteredSource.addFeatures(features);
    } else {
      this.toastService.showAlertWithHeader('No stations available',
        'Due to the filter selection, there are no ISMN points available.')
    }
    this.noIsmnPoints.emit(features.length == 0);
  }

  ngAfterViewInit(): void {
    if (!this.Map) {
      this.zone.runOutsideAngular(() => this.initMap());
    }
    setTimeout(() => this.mapReady.emit(this.Map));
  }

  private initMap(): void {
    addCommonProjections();
    let mapProjectionString = 'EPSG:3857';
    this.projection = GetProjection(mapProjectionString);
    this.view = new View({
      center: transform(this.center, 'EPSG:4326', 'EPSG:3857'),
      zoom: this.zoom,
      projection: this.projection,
    });


    const styleFunction = (feature) => {

      let markerColor = '#808080'; // Default color: gray
      const numberOfLocations = this.checkNumberOfLocations(feature.get('features'))
      if (feature.get('features') != undefined) {
        //function called from a cluster source
        if (feature.get('features').length > 1 && numberOfLocations > 1) {
          //clustered representation of multiple points

          return new Style({
            image: new Circle({
              radius: this.multipleSensorMarkerRadius,
              stroke: new Stroke({
                color: this.multipleSensorStrokeColor,
                width: this.multipleSensorStrokeWidth,
              })
            })
          });

        } else if (feature.get('features').length > 1 && numberOfLocations === 1) {
          return new Style({
            image: new Circle({
              radius: this. singleLocationMarkerRadius,
              stroke: new Stroke({
                color: this.singleLocationStrokeColor,
                width: this. singleLocationStrokeWidth,
              })
            })
          });
        } else {
          return new Style({
            image: new Circle({
              radius: this.singleSensorMarkerRadius,
              fill: new Fill({color: this.singleLocationStrokeColor})
            })
          });
        }
      } else {
        return new Style({
          image: new Circle({
            radius: 5,
            fill: new Fill({color: this.singleLocationStrokeColor})
          })
        });
      }
    };

    let clusterSource = new Cluster({
      source: this.clusteredSource,
      distance: 20 // Pixel distance between features to be clustered
    });

    let clusteredSourceLayer = new VectorLayer({
      source: clusterSource,
      style: styleFunction,
    });

    let nonClusteredSourceLayer = new VectorLayer({
      source: this.nonClusteredSource,
      style: styleFunction,
    });


    const tooltip = this.elementRef.nativeElement.querySelector('#tooltip');
    const tooltipContent = this.elementRef.nativeElement.querySelector('#tooltip-content');

    let tooltipOverlay = new Overlay({
      element: tooltip,
      positioning: 'bottom-center',
      stopEvent: false,
      offset: [0, -10],
    });


    this.Map = new Map({
      layers: [new TileLayer({
        source: new OSM({})
      }), clusteredSourceLayer, nonClusteredSourceLayer],
      target: 'map',
      controls: [new Attribution({collapsible: true})],
      view: this.view,
    });
    this.Map.addControl(new BoundingBoxControl(this.Map, this.spatialSubset, this.toastService, this.zone));
    this.Map.addOverlay(tooltipOverlay);

    this.Map.addOverlay(tooltipOverlay);

    this.Map.on('pointermove', (evt) =>{
      const feature  = this.Map.forEachFeatureAtPixel(evt.pixel, (feature) => {
        return feature
      })

      if (feature) {
        this.Map.getTargetElement().style.cursor = 'pointer';
      } else {
        this.Map.getTargetElement().style.cursor = '';
      }

    })

    this.Map.on('click', (evt) => {
      this.zone.runOutsideAngular(() => {
        const features = [];
        this.Map.forEachFeatureAtPixel(evt.pixel, (feature) => {
          const sensorList = feature.get('features');

          if (feature.get('datasetProperties')) { // this branch covers simple polygons and points
            if (!features.includes(feature)) {
              features.push(feature);
            }
          } else if (sensorList) { //this branch covers cluster points
            sensorList.forEach(sensor => features.push(sensor))
          }
        });

        if (features.length > 0) {
          const coordinates = evt.coordinate;
          tooltipContent.innerHTML = this.generateSensorInformation(features);
          tooltipOverlay.setPosition(coordinates);
        } else {
          tooltipOverlay.setPosition(undefined);
        }
      });
    });
  }

  private getMultipleSensorInformation(sensors, numberOfLocations: number): string {
    const numberOfSensors = sensors.length;
    let textToReturn = '';
    if (numberOfLocations > 1) {
      textToReturn +=
        `There are ${numberOfSensors} sensors at ${numberOfLocations} locations. Zoom in to see more details.`
    } else {
      const stationProperties = sensors[0].get('datasetProperties');
      textToReturn +=
        `<div class="flex flex-row">
            <b class="mr-1">Station: </b><span>${this.getPropertyValue(stationProperties, this.propertyNames.station)}</span>
         </div>` +
        `<div class="flex flex-row">
            <b class="mr-1">Network: </b><span>${this.getPropertyValue(stationProperties, this.propertyNames.network)}</span>
         </div>` +
        `<div><b>Sensors details: </b></div>`
      sensors.forEach((sensor, index) => {
        const sensorProperties = sensor.get('datasetProperties');
        textToReturn += this.getSensorInformation(sensorProperties, index);

      })
    }

    return textToReturn
  }

  private getSensorInformation(sensorProperties, index: number): string {
    return `<div class="flex flex-row">
            <b class="mr-1">${index + 1}. </b>
            ${this.getPropertyValue(sensorProperties, this.propertyNames.depthFrom)}
              - ${this.getPropertyValue(sensorProperties, this.propertyNames.depthTo)} m;
              ${this.styleDate(this.getPropertyValue(sensorProperties, this.propertyNames.timeRangeFrom))}
              - ${this.styleDate(this.getPropertyValue(sensorProperties, this.propertyNames.timeRangeTo))}
         </div>`
  }

  private getPropertyValue(properties, propertyName): string {
    return properties.find(property => property.propertyName == propertyName).propertyValue
  }

  private styleDate(date: string): string {
    let dateAsDate = new Date(date);
    return dateAsDate ? dateAsDate.toLocaleDateString('en-US', {month: 'short', day: 'numeric', year: 'numeric'}) : null
  }


  private hexToRgba(hex, opacity): string {
    // Remove the hash character, if any
    hex = hex.replace('#', '');

    // Parse the hexadecimal value to get separate R, G, and B values
    let bigint = parseInt(hex, 16);
    let r = (bigint >> 16) & 255;
    let g = (bigint >> 8) & 255;
    let b = bigint & 255;

    // Calculate the alpha value (opacity)
    let alpha = opacity || 1.0;

    // Return the RGBA value
    return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + alpha + ')';
  }

  private checkNumberOfLocations(features): number {
    let coordinates = []
    features.forEach(feature => {
      let featureCoordinates = feature.getGeometry().getCoordinates();
      if (!coordinates.find(coords => coords.every((value, index) => value === featureCoordinates[index]))) {
        coordinates.push(featureCoordinates)
      }
    })
    return coordinates.length
  }

  private generateSensorInformation(features): string {
    const numberOfLocations = this.checkNumberOfLocations(features)
    if (features.length > 1) {
      return this.generateMultipleSensorInformation(features, numberOfLocations)
    } else {
      return this.generateSingleSensorTooltip(features[0]);
    }
  }


  private generateMultipleSensorInformation(features, numberOfLocations): string {
    return `<div class="flex flex-column text-base p-1 text-justify">
            ${this.getMultipleSensorInformation(features, numberOfLocations)}
            </div>`;
  }

  private generateSingleSensorTooltip(feature): string {
    const properties = feature.get('datasetProperties');
    return '<div class="flex flex-column text-base p-1 border-round-bottom-md"> ' +
      `<div class="flex flex-row">
            <b class="mr-1">Station: </b>
            <span>${this.getPropertyValue(properties, this.propertyNames.station)}</span>
        </div>` +
      `<div class="flex flex-row">
            <b class="mr-1">Network: </b>
            <span>${this.getPropertyValue(properties, this.propertyNames.network)}</span>
        </div>` +
      `<div><b>Sensor details: </b></div>` +
      this.getSensorInformation(properties, 0) +
      '</div>';
  }

}


