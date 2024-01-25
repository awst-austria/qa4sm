import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  NgZone,
  OnInit,
  Output
} from '@angular/core';
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
  styleUrls: ['./map.component.scss']
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

  singleSensorMarkerRadius = 5;
  multipleSensorMarkerRadius = 8;
  multipleSensorStrokeColor = 'blue';
  multipleSensorStrokeWidth = 2;
  legendItems: LegendItem[];

  constructor(private zone: NgZone, private cd: ChangeDetectorRef, private toastService: ToastService, private elementRef: ElementRef) {
  }

  ngOnInit() {
    this.legendItems = [
      {
        label: "Multiple sensors",
        tooltip: 'Location with multiple sensors. Zoom in to see single sensor. ',
        strokeColor: this.multipleSensorStrokeColor,
        radius: this.multipleSensorMarkerRadius,
        strokeWidth: this.multipleSensorStrokeWidth,
      },
      {
        label: 'Single Sensor',
        tooltip: 'Location with a single sensor. Different colors indicate different networks. Hover over the point to find out more about the sensor.',
        strokeWidth: 0,
        fillColor: 'black',
        strokeColor: 'black',
        radius: this.singleSensorMarkerRadius
      },
    ];
  }

  public clearSelection() {
    this.clusteredSource.clear();
    this.nonClusteredSource.clear();
  }

  public addGeoJson(geoJson: string) {
    console.log("ADD geojson-----------------------------------------------------");
    let features = new GeoJSON().readFeatures(geoJson, {
      dataProjection: 'EPSG:4326',
      featureProjection: 'EPSG:3857'
    });

    if (features.length > 0 && features[0].getGeometry().getType() === 'Polygon') {
      //Satellite datasets
      this.nonClusteredSource.addFeatures(features);
    } else {
      //ISMN
      this.clusteredSource.addFeatures(features);
    }
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
    // this.projection.setExtent(this.extent);
    this.view = new View({
      center: transform(this.center, 'EPSG:4326', 'EPSG:3857'),
      zoom: this.zoom,
      projection: this.projection,
    });


    const styleFunction = (feature) => {

      let markerColor = '#808080'; // Default color: gray

      if (feature.get('features') != undefined) {
        //function called from a cluster source
        if (feature.get('features').length > 1) {
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


        } else {
          if (feature.get('features')[0].get('markerColor') != undefined) {
            markerColor = feature.get('features')[0].get('markerColor');
          }

          return new Style({
            image: new Circle({
              radius: this.singleSensorMarkerRadius,
              fill: new Fill({color: markerColor})
            })
          });
        }
      } else {
        let markerColor = feature.get('markerColor');

        // If the markerColor property doesn't exist or is not a valid color, set a default color.
        if (!markerColor) {
          markerColor = '#808080';
        }

        if (feature.getGeometry().getType() === 'Polygon') {
          return new Style({
            stroke: new Stroke({
              color: 'blue',
              lineDash: [4],
              width: 1,
            }),
            fill: new Fill({
              color: this.hexToRgba(markerColor, 0.5),
            }),
          })
        }

        return new Style({
          image: new Circle({
            radius: 5,
            fill: new Fill({color: markerColor})
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

    //map.addOverlay(tooltipOverlay);
//----


    this.Map = new Map({
      layers: [new TileLayer({
        source: new OSM({})
      }), clusteredSourceLayer, nonClusteredSourceLayer],
      target: 'map',
      // controls: DefaultControls({attribution: false}).extend([new MyControl(),new Attribution({collapsible: true,})]),
      controls: [new Attribution({collapsible: true})],
      view: this.view,
    });
    this.Map.addControl(new BoundingBoxControl(this.Map, this.spatialSubset, this.toastService, this.zone));
    this.Map.addOverlay(tooltipOverlay);
    for (let vec in this.Map.getAllLayers()) {
      console.log('LAyer: ', vec)
    }


    this.Map.addOverlay(tooltipOverlay);

    this.Map.on('pointermove', (evt) => {
      this.zone.runOutsideAngular(() => {
        const features = [];
        this.Map.forEachFeatureAtPixel(evt.pixel, (feature) => {
          if (feature.get('datasetProperties')) { // this branch covers simple polygons and points
            if (!features.includes(feature)) {
              features.push(feature);
            }
          } else if (feature.get('features')) { //this branch covers cluster points
            if (feature.get('features').length == 1) {
              if (!features.includes(feature.get('features')[0])) {
                features.push(feature.get('features')[0]);
              }
            } else {
              console.log(feature.get('features'))
            }
          }
        });

        if (features.length > 0) {
          const coordinates = evt.coordinate;
          tooltipContent.innerHTML = this.generateMultipleTables(features);
          tooltipOverlay.setPosition(coordinates);
        } else {
          tooltipOverlay.setPosition(undefined);
        }
      });
    });
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

  private generateMultipleTables(features): string {
    let combinedTableHTML = '';
    features.forEach(feature => {
      const properties = feature.get('datasetProperties');
      let tableHTML = '<table>';
      let textHTML = '<div class="flex flex-row">Station information:</div>';

      // Add the table header
      tableHTML += `
        <thead>
          <tr>
            <th>Property</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
      `;

      properties.forEach(property => {
        tableHTML += `
          <tr>
            <td>${property.propertyName}</td>
            <td>${property.propertyValue}</td>
          </tr>
        `;
        textHTML += `<div class="flex flex-row"><b>${this.stylePropertyName(property.propertyName)}:</b> ${property.propertyValue}</div>`
      });

      tableHTML += '</tbody></table>';
      combinedTableHTML += '<div class="flex flex-column">' + textHTML + '</div>';
    });

    return combinedTableHTML;
  }

  stylePropertyName(propertyName: string): string{
    return propertyName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
}


