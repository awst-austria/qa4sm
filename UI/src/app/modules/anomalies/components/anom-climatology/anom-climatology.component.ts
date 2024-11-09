import {Component, model} from '@angular/core';
import {AnomaliesModel} from '../anomalies/anomalies-model';

@Component({
  selector: 'qa-anom-climatology',
  templateUrl: './anom-climatology.component.html',
  styleUrls: ['./anom-climatology.component.scss']
})
export class AnomClimatologyComponent  {
  public minYear = 1971;
  public maxYear = 2100;

  anomaliesModel = model({} as AnomaliesModel);

  constructor() {
  }
}
