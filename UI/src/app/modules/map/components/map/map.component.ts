import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  NgZone,
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
import {Icon, Stroke} from "ol/style";
import {Style, Circle, Fill} from 'ol/style';
import {addCommon as addCommonProjections} from 'ol/proj.js';
import {Cluster} from "ol/source";

@Component({
  selector: 'qa-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.scss']
})
export class MapComponent implements AfterViewInit {

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


  geojsonObject = {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "MultiPoint",
          "coordinates": [
            [12.3155, 45.4408],
            [12.3195, 45.4408],
            [12.3235, 45.4408],
            [12.3275, 45.4408]
          ]
        },
        "properties": {
          "datasetName": "exampleDataset",
          "datasetVersion": "1.0",
          "datasetProperties": [
            {"propertyName": "prop1", "propertyValue": "value1"},
            {"propertyName": "prop2", "propertyValue": "value2"},
            {"propertyName": "prop3", "propertyValue": "value3"}
          ]
        }
      },
      {
        "type": "Feature",
        "geometry": {
          "type": "MultiPoint",
          "coordinates": [
            [12.3155, 45.4518],
            [12.3195, 45.4518],
            [12.3235, 45.4518],
            [12.3275, 45.4518]
          ]
        },
        "properties": {
          "datasetName": "exampleDataset",
          "datasetVersion": "2.0",
          "datasetProperties": [
            {"propertyName": "prop1", "propertyValue": "value1"},
            {"propertyName": "prop2", "propertyValue": "value2"},
            {"propertyName": "prop3", "propertyValue": "value3"},
            {"markerColor": "#FF5733"}
          ]
        }
      },
      {
        "type": "Feature",
        "geometry": {
          "type": "MultiPoint",
          "coordinates": [
            [12.3155, 45.4628],
            [12.3195, 45.4628],
            [12.3235, 45.4628],
            [12.3275, 45.4628]
          ]
        },
        "properties": {
          "datasetName": "exampleDataset",
          "datasetVersion": "3.0",
          "datasetProperties": [
            {"propertyName": "prop1", "propertyValue": "value1"},
            {"propertyName": "prop2", "propertyValue": "value2"},
            {"propertyName": "prop3", "propertyValue": "value3"},
            {"markerColor": "#33FF57"}
          ]
        }
      }
    ]
  }


  constructor(private zone: NgZone, private cd: ChangeDetectorRef, private toastService: ToastService, private elementRef: ElementRef) {
  }


  public clearSelection() {
    this.clusteredSource.clear();
    this.nonClusteredSource.clear();
  }

  public addGeoJson(geoJson: string) {
    console.log("ADD geojson-----------------------------------------------------");
    var features = new GeoJSON().readFeatures(geoJson, {
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
      // extent: [-572513.341856, 5211017.966314, 916327.095083, 6636950.728974]
    });


    const styleFunction = (feature) => {

      let markerColor = '#808080'; // Default color: gray

      if (feature.get('features') != undefined) {
        //function called from a cluster source

        // console.log("Feature count: " + feature.get('features').length, feature.get('features'))
        if (feature.get('features').length > 1) {
          //clustered representation of multiple points

          return new Style({
            image: new Circle({
              radius: 8,
              stroke: new Stroke({
                color: 'blue',
                width: 2,
              })
            })
          });


        } else {
          if (feature.get('features')[0].get('markerColor') != undefined) {
            markerColor = feature.get('features')[0].get('markerColor');
          }
          return new Style({
            image: new Circle({
              radius: 5,
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

    var clusterSource = new Cluster({
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
    for (var vec in this.Map.getAllLayers()) {
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
          }
          else if(feature.get('features')){ //this branch covers cluster points
            if(feature.get('features').length==1){
              if (!features.includes(feature.get('features')[0])) {
                features.push(feature.get('features')[0]);
              }
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
    var bigint = parseInt(hex, 16);
    var r = (bigint >> 16) & 255;
    var g = (bigint >> 8) & 255;
    var b = bigint & 255;

    // Calculate the alpha value (opacity)
    var alpha = opacity || 1.0;

    // Return the RGBA value
    return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + alpha + ')';
  }

  private generateMultipleTables(features): string {
    let combinedTableHTML = '';

    console.log("Features: ", features)
    features.forEach(feature => {
      console.log("Feature: ", feature)
      const properties = feature.get('datasetProperties');
      let tableHTML = '<table>';

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
      });

      tableHTML += '</tbody></table>';
      combinedTableHTML += tableHTML;
    });

    return combinedTableHTML;
  }
}


