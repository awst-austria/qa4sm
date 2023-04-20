import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ScalingComponent} from './scaling.component';
import {BehaviorSubject} from 'rxjs';

describe('ScalingComponent', () => {
  let component: ScalingComponent;
  let fixture: ComponentFixture<ScalingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ScalingComponent]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ScalingComponent);
    component = fixture.componentInstance;
    component.validationModel = {
      datasetConfigurations: [],
      referenceConfigurations: null,
      spatialSubsetModel: null,
      validationPeriodModel: null,
      metrics: [],
      anomalies: null,
      temporalMatchingModel: null,
      scalingMethod: null,
      nameTag$: new BehaviorSubject('')
    };
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
