import { Component, OnInit } from '@angular/core';
import { MapModule } from '../../../map/map.module';
import { Map, View } from 'ol';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import { Cluster } from 'ol/source';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';


@Component({
  selector: 'qa-interactive-map',
  standalone: true,
  imports: [
    MapModule
  ],
  templateUrl: './interactive-map.component.html',
  styleUrl: './interactive-map.component.scss'
})
export class InteractiveMapComponent implements OnInit {
  Map: Map;
  clusteredSource: VectorSource = new VectorSource();


  ngOnInit() {
    console.log('InteractiveMapComponent init');
    this.initMap();
  }

  private initMap() {

    let clusterSource = new Cluster({
      source: this.clusteredSource,
      distance: 20 // Pixel distance between features to be clustered
    });

    let clusteredSourceLayer = new VectorLayer({
      source: clusterSource,
    });


    this.Map = new Map({
      target: 'map',
      layers: [new TileLayer({
        source: new OSM({})
      }), clusteredSourceLayer],
      view: new View({
        projection: 'EPSG:3857',
        center: [0, 0],
        zoom: 2,
        minZoom: 0,
        maxZoom: 18
      }),
      controls: []
    })
  }

}
