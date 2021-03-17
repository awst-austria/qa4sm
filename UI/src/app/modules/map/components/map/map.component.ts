import {AfterViewChecked, AfterViewInit, ChangeDetectorRef, Component, EventEmitter, Input, NgZone, Output} from '@angular/core';
import {Map, View} from 'ol';
import {Coordinate} from 'ol/coordinate';
import {Attribution, Control} from 'ol/control';
import Projection from 'ol/proj/Projection';
import {register} from 'ol/proj/proj4';
import {get as GetProjection} from 'ol/proj';
import {Extent} from 'ol/extent';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';

// import * as proj4 from 'proj4';
// import {proj4} from 'proj4';
import * as proj4x from 'proj4';
import Draw, {createBox} from 'ol/interaction/Draw';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import GeometryType from 'ol/geom/GeometryType';

const proj4 = (proj4x as any).default;

@Component({
  selector: 'qa-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.scss']
})
export class MapComponent implements AfterViewInit, AfterViewChecked {

  @Input() center: Coordinate;
  @Input() zoom: number;
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

  ngAfterViewChecked(): void {
    console.log('View checked');
  }

  private initMap(): void {
    proj4.defs('EPSG:3857', '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs');
    proj4.defs('EPSG:4326', '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs');

    register(proj4);
    this.projection = GetProjection('EPSG:3857');
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
      controls: [new MyControl(this.Map), new Attribution({collapsible: true,})],
      view: this.view,
    });
  }

  // controls: DefaultControls().extend([
  //                                      new ScaleLine({}),
  //                                    ]),
}

export class MyControl extends Control {
  constructor(private map) {
    super({});
    let button = document.createElement('button');
    button.type = 'button';
    button.innerHTML = '<i class="pi pi-pencil"></i>';
    button.title = 'Select region';

    let element = document.createElement('div');
    element.className = 'rotate-north ol-unselectable ol-control';
    element.appendChild(button);
    Control.call(this, {
      element: element
    });
    button.addEventListener('click', () => this.click());
  }

  click() {
    console.log('click');
    console.log(this.getMap());
    var source = new VectorSource({wrapX: false});

    var vector = new VectorLayer({
      source: source,
    });
    let geomFunction = createBox();
    let draw = new Draw({
      source: source,
      type: GeometryType.CIRCLE,
      geometryFunction: geomFunction,
    });
    this.getMap().addLayer(vector);
    this.getMap().addInteraction(draw);

  }

}
