import {Component, Input, OnInit} from '@angular/core';
import {AnomaliesModel} from '../anomalies/anomalies-model';

@Component({
  selector: 'qa-anom-climatology',
  templateUrl: './anom-climatology.component.html',
  styleUrls: ['./anom-climatology.component.scss']
})
export class AnomClimatologyComponent implements OnInit {
  public minYear = 1971;
  public maxYear = 2100;

  @Input() anomaliesModel: AnomaliesModel;

  constructor() {
  }

  ngOnInit(): void {
  }

  setDate(year): Date {
    return new Date(`${year}-01-01`);
 }

  getYearFrom(): number {
    let year: number;
    this.anomaliesModel.anomaliesFrom$.subscribe(date => {
      date ? year = date.getFullYear() : year = this.minYear;
    });
    return year;
 }

  getYearTo(): number {
    let year: number;
    this.anomaliesModel.anomaliesTo$.subscribe(date => {
      date ? year = date.getFullYear() : year = (new Date()).getFullYear();
    });
    return year;
  }

}
