import {Component, Input, OnInit} from '@angular/core';
import {AnomaliesModel} from './anomalies-model';

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
  readonly anomaliesNoneID: string = ANOMALIES_NONE;
  readonly anomaliesClimatologyID: string = ANOMALIES_CLIMATOLOGY;
  readonly anomalies35DMaID: string = ANOMALIES_35D_MA;

  availableAnomalyMethodModels: AnomaliesModel[] = [];
  selectedMethod: AnomaliesModel;

  @Input() methodForValidation: AnomaliesModel;

  constructor() {
  }

  ngOnInit(): void {
    this.prepareAnomaliesMethodModels();
  }

  selectedMethodChanged() {
    this.methodForValidation.id = this.selectedMethod.id;
    this.methodForValidation.anomaliesFrom = this.selectedMethod.anomaliesFrom;
    this.methodForValidation.anomaliesTo = this.selectedMethod.anomaliesTo;
  }

  private prepareAnomaliesMethodModels() {
    this.availableAnomalyMethodModels.push(new AnomaliesModel(ANOMALIES_NONE, ANOMALIES_NONE_DESC));
    this.availableAnomalyMethodModels.push(new AnomaliesModel(ANOMALIES_35D_MA, ANOMALIES_35D_MA_DESC));
    this.availableAnomalyMethodModels.push(new AnomaliesModel(ANOMALIES_CLIMATOLOGY, ANOMALIES_CLIMATOLOGY_DESC));
    this.selectedMethod = this.availableAnomalyMethodModels[0];
  }

}
