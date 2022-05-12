import {Component, Input, OnInit} from '@angular/core';
import {TemporalMatchingModel} from './temporal-matching-model';
import {BehaviorSubject} from 'rxjs';


export const SIZE_1 = 1;
export const SIZE_1_DESC = '1 hour';

export const SIZE_6 = 6;
export const SIZE_6_DESC = '6 hours';

export const SIZE_12 = 12;
export const SIZE_12_DESC = '12 hours';

export const SIZE_24 = 24;
export const SIZE_24_DESC = '24 hours';

@Component({
  selector: 'qa-temporal-matching',
  templateUrl: './temporal-matching.component.html',
  styleUrls: ['./temporal-matching.component.scss']
})
export class TemporalMatchingComponent implements OnInit {

  // these fields are required because templates have no access to constants
  readonly size1: number = SIZE_1;
  readonly size6: number = SIZE_6;
  readonly size12: number = SIZE_12;
  readonly size24: number = SIZE_24;

  availableTemporalMatchingModels: TemporalMatchingModel[] = [];
  selectedSize$: BehaviorSubject<TemporalMatchingModel> = new BehaviorSubject<TemporalMatchingModel>(null);

  @Input() temporalMatchingModel: TemporalMatchingModel;

  constructor() {
  }

  public setSelection(sizeValue: number): void {
    this.availableTemporalMatchingModels.forEach(temporalMatchingModel => {
      if (temporalMatchingModel.size$.getValue() === sizeValue) {
        this.selectedSize$.next(temporalMatchingModel);
      }
    });
  }

  ngOnInit(): void {
    this.prepareAnomaliesMethodModels();
    this.selectedSize$.subscribe(value => {
      this.temporalMatchingModel.size$.next(value.size$.getValue());
    });
  }

  private prepareAnomaliesMethodModels(): void {
    this.availableTemporalMatchingModels.push(
      new TemporalMatchingModel(
        new BehaviorSubject<number>(SIZE_1),
        SIZE_1_DESC,
      )
    );
    this.availableTemporalMatchingModels.push(
      new TemporalMatchingModel(
        new BehaviorSubject<number>(SIZE_6),
        SIZE_6_DESC,
      )
    );
    this.availableTemporalMatchingModels.push(
      new TemporalMatchingModel(
        new BehaviorSubject<number>(SIZE_12),
        SIZE_12_DESC,
      )
    );
    this.availableTemporalMatchingModels.push(
      new TemporalMatchingModel(
        new BehaviorSubject<number>(SIZE_24),
        SIZE_24_DESC,
      )
    );

    this.selectedSize$.next(this.availableTemporalMatchingModels[0]);
  }

}
