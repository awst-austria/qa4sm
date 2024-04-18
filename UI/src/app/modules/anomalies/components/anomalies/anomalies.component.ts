import {Component, Input, OnInit} from '@angular/core';
import {AnomaliesModel} from './anomalies-model';
import {BehaviorSubject} from 'rxjs';

// The following constants come from the validation_run database model
export const ANOMALIES_NONE: string = 'none';
export const ANOMALIES_NONE_DESC: string = 'Do not calculate';

export const ANOMALIES_CLIMATOLOGY: string = 'climatology';
export const ANOMALIES_CLIMATOLOGY_DESC: string = 'Climatology';

export const ANOMALIES_35D_MA: string = 'moving_avg_35_d';
export const ANOMALIES_35D_MA_DESC: string = '35 day moving average';

@Component({
  selector: 'qa-anomalies',
  templateUrl: './anomalies.component.html',
  styleUrls: ['./anomalies.component.scss']
})
export class AnomaliesComponent implements OnInit {

  // these fields are required because templates have no access to constants
  readonly anomaliesClimatology: string = ANOMALIES_CLIMATOLOGY;

  availableAnomalyMethodModels: AnomaliesModel[] = [];
  selectedMethod$: BehaviorSubject<AnomaliesModel> = new BehaviorSubject<AnomaliesModel>(null);

  @Input() anomaliesModel: AnomaliesModel;

  constructor() {
  }

  public setSelection(anomaliesMethodName: string): void {
    this.availableAnomalyMethodModels.forEach(anomalyModel => {
      if (anomalyModel.method$.getValue() == anomaliesMethodName) {
        this.selectedMethod$.next(anomalyModel);
      }
    });
  }

  ngOnInit(): void {
    this.prepareAnomaliesMethodModels();
    this.selectedMethod$.subscribe(value => {
      this.anomaliesModel.method$.next(value.method$.getValue());
      this.anomaliesModel.anomaliesFrom$.next(value.anomaliesFrom$.getValue());
      this.anomaliesModel.anomaliesTo$.next(value.anomaliesTo$.getValue());
    });
  }


  private prepareAnomaliesMethodModels() {
    this.availableAnomalyMethodModels.push(
      new AnomaliesModel(
        new BehaviorSubject<string>(ANOMALIES_NONE),
        ANOMALIES_NONE_DESC,
        new BehaviorSubject<Date>(null),
        new BehaviorSubject<Date>(null)));
    this.availableAnomalyMethodModels.push(
      new AnomaliesModel(
        new BehaviorSubject<string>(ANOMALIES_35D_MA),
        ANOMALIES_35D_MA_DESC,
        new BehaviorSubject<Date>(null),
        new BehaviorSubject<Date>(null)));

    let climatology = new AnomaliesModel(
      new BehaviorSubject<string>(ANOMALIES_CLIMATOLOGY),
      ANOMALIES_CLIMATOLOGY_DESC,
      new BehaviorSubject<Date>(null),
      new BehaviorSubject<Date>(null));

    climatology.anomaliesTo$.subscribe(newToDate => {
      this.anomaliesModel.anomaliesTo$.next(newToDate);
    });
    climatology.anomaliesFrom$.subscribe(newFromDate => {
      this.anomaliesModel.anomaliesFrom$.next(newFromDate);
    });

    this.availableAnomalyMethodModels.push(climatology);

    this.selectedMethod$.next(this.availableAnomalyMethodModels[0]);
  }

}
