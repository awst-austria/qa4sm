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
  selectedDatasets: VectorSource = new VectorSource();
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


  public clearSelection(){
    this.selectedDatasets.clear();
  }

  public addGeoJson(geoJson: string) {
    this.selectedDatasets.addFeatures(new GeoJSON().readFeatures(geoJson, {
      dataProjection: 'EPSG:4326',
      featureProjection: 'EPSG:3857'
    }));
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
      let markerColor = feature.get('markerColor');

      // If the markerColor property doesn't exist or is not a valid color, set a default color.
      if (!markerColor) {
        markerColor = '#808080';  // Default color: gray
      }


      console.log("Geo GEOM: "+feature.getGeometry().getType())
        if(feature.getGeometry().getType()==='Point'||feature.getGeometry().getType()==='MultiPoint'){
            return new Style({
                image: new Circle({
                    radius: 5,
                    fill: new Fill({color: markerColor})
                })
            });
        }
        else if(feature.getGeometry().getType()==='Polygon'){
            return new Style({
                stroke: new Stroke({
                    color: 'blue',
                    lineDash: [4],
                    width: 3,
                }),
                fill: new Fill({
                    color: markerColor,
                }),
            })
        }

        console.error("Unknown geometry type: "+feature.getGeometry().getType())
        return null;
    };

    this.addGeoJson(JSON.stringify(this.geojsonObject));
    let vectorLayer = new VectorLayer({
      source: this.selectedDatasets,
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
      }), vectorLayer],
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
          if (feature.get('datasetProperties')) {
            if(!features.includes(feature)){
              features.push(feature);
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

  private generateMultipleTables(features): string {
    let combinedTableHTML = '';

    console.log("Features: ",features)
    features.forEach(feature => {
      console.log("Feature: ",feature)
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


