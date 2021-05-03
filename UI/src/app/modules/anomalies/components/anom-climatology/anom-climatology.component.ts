import {Component, Input, OnInit} from '@angular/core';
import {AnomaliesModel} from '../anomalies/anomalies-model';

@Component({
  selector: 'qa-anom-climatology',
  templateUrl: './anom-climatology.component.html',
  styleUrls: ['./anom-climatology.component.scss']
})
export class AnomClimatologyComponent implements OnInit {

  @Input() anomaliesModel: AnomaliesModel;

  constructor() {
  }

  ngOnInit(): void {
  }

}
