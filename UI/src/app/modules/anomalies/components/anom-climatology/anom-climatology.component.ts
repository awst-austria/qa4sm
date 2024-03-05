import {Component, Input} from '@angular/core';
import {AnomaliesModel} from '../anomalies/anomalies-model';

@Component({
  selector: 'qa-anom-climatology',
  templateUrl: './anom-climatology.component.html',
  styleUrls: ['./anom-climatology.component.scss']
})
export class AnomClimatologyComponent  {
  public minYear = 1971;
  public maxYear = 2100;

  @Input() anomaliesModel: AnomaliesModel;

  constructor() {
  }

  setDate(year): Date {
    return new Date(`${year}-01-01`);
 }

  getYearFrom(): number {
    let year: number;
    if (this.anomaliesModel.anomaliesFrom$.getValue()){
      year = this.anomaliesModel.anomaliesFrom$.getValue().getFullYear();
    } else {
      year = this.minYear;
      this.anomaliesModel.anomaliesFrom$.next(this.setDate(year));
    }

    return year;
 }

  getYearTo(): number {
    let year: Date;

    if (this.anomaliesModel.anomaliesTo$.getValue()){
      year = this.anomaliesModel.anomaliesTo$.getValue();
    } else {
      year = (new Date());
      this.anomaliesModel.anomaliesTo$.next(year);
    }
    return year.getFullYear();
  }

}
