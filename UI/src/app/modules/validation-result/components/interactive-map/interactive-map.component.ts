import { Component, input, OnInit } from '@angular/core';
import { MapModule } from '../../../map/map.module';
import { Map, View } from 'ol';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import { Cluster } from 'ol/source';
import VectorSource from 'ol/source/Vector';
import { FullScreen } from 'ol/control';
import { WebsiteGraphicsService } from '../../../core/services/global/website-graphics.service';


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
  validationId = input('');

  Map: Map;
  clusteredSource: VectorSource = new VectorSource();

  constructor(public plotService: WebsiteGraphicsService) {
  }


  ngOnInit() {
    this.initMap();
  }

  private initMap() {

    let clusterSource = new Cluster({
      source: this.clusteredSource,
      distance: 20 // Pixel distance between features to be clustered
    });

    this.Map = new Map({
      target: 'map',
      layers: [new TileLayer({
        source: new OSM({})
      })],
      view: new View({
        projection: 'EPSG:3857',
        center: [0, 0],
        zoom: 2,
        minZoom: 0,
        maxZoom: 18
      }),
      controls: [
        new FullScreen()
      ]
    });
    this.loadAvailableLayers();
  }

  private loadAvailableLayers(){
  //   here goes the logic for fetching and managing layers
    this.plotService.getAvailableTiffLayers(this.validationId()).subscribe(
      //   here add what should happen with the given layers; it might be a good idea to define an interface for the layer
      data => {console.log(data)}
    )
  }

}
