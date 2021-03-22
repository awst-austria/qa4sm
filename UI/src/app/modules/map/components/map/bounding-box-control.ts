import {Control} from 'ol/control';
import VectorSource from 'ol/source/Vector';
import Draw, {createBox} from 'ol/interaction/Draw';
import {Map} from 'ol';
import VectorLayer from 'ol/layer/Vector';
import GeometryType from 'ol/geom/GeometryType';
import {transformExtent} from 'ol/proj';
import {SpatialSubsetModel} from '../../../spatial-subset/components/spatial-subset/spatial-subset-model';
import {NgZone} from '@angular/core';

export class BoundingBoxControl extends Control {
  boundingBoxSource: VectorSource;
  bboxDraw: Draw = null;
  currentSelectedCoordinates: SpatialSubsetModel;
  ngZone: NgZone;

  constructor(private map: Map, private boundingBox: SpatialSubsetModel, ngZone?: NgZone) {
    super({});
    this.ngZone = ngZone;
    //Prepare Source and Layer for the bounding box drawn by the user
    this.boundingBoxSource = new VectorSource({wrapX: false});
    map.addLayer(new VectorLayer({
      source: this.boundingBoxSource,
    }));


    // This is the actual pencil icon shown in the top left corner of the map
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

    this.boundingBox.maxLat$.subscribe(next => this.updateBoundingBox());
    this.boundingBox.maxLon$.subscribe(next => this.updateBoundingBox());
    this.boundingBox.minLat$.subscribe(next => this.updateBoundingBox());
    this.boundingBox.minLon$.subscribe(next => this.updateBoundingBox());
  }


  private updateBoundingBox() {
    // Since openlayers is not an angular component, events that are coming from it wont trigger an update in
    // templates. As a workaround we run an empty method in the ngZone which then triggers the template updates.
    //https://github.com/angular/angular/issues/35579
    //https://github.com/angular/angular/issues/35579#issuecomment-589449820
    this.ngZone.run(() => {
    });

    if (this.isCoordinateValid(this.boundingBox.maxLat$.getValue(), this.boundingBox.maxLon$.getValue()) &&
      this.isCoordinateValid(this.boundingBox.minLat$.getValue(), this.boundingBox.minLon$.getValue())) {
      //TODO to be implemented
      console.log('Implement map update. ');
    }


  }

  private isCoordinateValid(lat: number, lon: number): boolean {
    if (lat == null || lon == null) {
      return false;
    }
    if (lat < -90 || lat > 90) {
      return false;
    }
    if (lon < -180 || lon > 180) {
      return false;
    }
    return true;
  }

  click() {

    //if a draw action is in progress then just remove it from the map.
    //this is basically cancel drawing
    if (this.bboxDraw != null) {
      this.getMap().removeInteraction(this.bboxDraw);
      this.bboxDraw = null;
      this.boundingBox.maxLat$.next(null);
      this.boundingBox.maxLon$.next(null);
      this.boundingBox.minLat$.next(null);
      this.boundingBox.minLon$.next(null);
      return;
    }

    //remove previous selection from map
    this.boundingBoxSource.clear();

    let geomFunction = createBox();
    this.bboxDraw = new Draw({
      source: this.boundingBoxSource,
      type: GeometryType.CIRCLE,
      geometryFunction: geomFunction,
    });

    this.getMap().addInteraction(this.bboxDraw);
    this.bboxDraw.on('drawend', evt => {
      //the map uses EPSG:3857 projection while the backend expects the coordinates in EPSG:4326 which means first we need to transform
      //the bounding box coordinates
      let bbCoordinates = transformExtent(evt.feature.getGeometry().getExtent(),
        this.getMap().getView().getProjection().getCode(),
        'EPSG:4326');

      //then update the model.
      this.boundingBox.minLon$.next(bbCoordinates[0]);
      this.boundingBox.minLat$.next(bbCoordinates[1]);
      this.boundingBox.maxLon$.next(bbCoordinates[2]);
      this.boundingBox.maxLat$.next(bbCoordinates[3]);

      this.getMap().removeInteraction(this.bboxDraw);
      this.bboxDraw = null;
    });

  }
}
