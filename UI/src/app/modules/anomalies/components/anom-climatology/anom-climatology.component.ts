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

  // @Input() anomaliesModel: AnomaliesModel;
  anomaliesModel = model({} as AnomaliesModel);

  constructor() {
  }

  setDate(year: number): Date {
    console.log(year);
    return new Date(`${year}-01-01`);
 }

 //  getYearFrom(): number {
 //    let year: number;
 //    if (this.anomaliesModel.anomaliesFrom()){
 //      year = this.anomaliesModel.anomaliesFrom().getFullYear();
 //    } else {
 //      year = this.minYear;
 //      this.anomaliesModel.anomaliesFrom.set(this.setDate(year));
 //    }
 //
 //    return year;
 // }

  // getYearTo(): number {
  //   let year: Date;
  //
  //   if (this.anomaliesModel.anomaliesTo()){
  //     year = this.anomaliesModel.anomaliesTo();
  //   } else {
  //     year = (new Date());
  //     this.anomaliesModel.anomaliesTo.set(year);
  //   }
  //   return year.getFullYear();
  // }

}
