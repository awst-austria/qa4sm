import {AfterViewInit, ChangeDetectorRef, Component, EventEmitter, Input, NgZone, Output} from '@angular/core';
import {Map, View} from 'ol';
import {Coordinate} from 'ol/coordinate';
import {Attribution} from 'ol/control';
import Projection from 'ol/proj/Projection';
import {register} from 'ol/proj/proj4';
import {get as GetProjection} from 'ol/proj';
import {Extent} from 'ol/extent';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';

import * as proj4x from 'proj4';
import {BoundingBoxControl} from './bounding-box-control';
import {SpatialSubsetModel} from '../../../spatial-subset/components/spatial-subset/spatial-subset-model';

const proj4 = (proj4x as any).default;

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
  @Output() mapReady = new EventEmitter<Map>();

  constructor(private zone: NgZone, private cd: ChangeDetectorRef) {
  }

  ngAfterViewInit(): void {
    console.log('View init');
    if (!this.Map) {
      this.zone.runOutsideAngular(() => this.initMap());
    }
    setTimeout(() => this.mapReady.emit(this.Map));
  }

  private initMap(): void {
    proj4.defs('EPSG:3857', '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs');
    proj4.defs('EPSG:4326', '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs');

    register(proj4);
    let mapProjectionString = 'EPSG:3857';
    this.projection = GetProjection(mapProjectionString);
    this.projection.setExtent(this.extent);
    this.view = new View({
      center: this.center,
      zoom: this.zoom,
      projection: this.projection,
      // extent: [-572513.341856, 5211017.966314, 916327.095083, 6636950.728974]
    });
    this.Map = new Map({
      layers: [new TileLayer({
        source: new OSM({})
      })],
      target: 'map',
      // controls: DefaultControls({attribution: false}).extend([new MyControl(),new Attribution({collapsible: true,})]),
      controls: [new Attribution({collapsible: true,})],
      view: this.view,
    });
    this.Map.addControl(new BoundingBoxControl(this.Map, this.spatialSubset, this.zone));
  }


}


