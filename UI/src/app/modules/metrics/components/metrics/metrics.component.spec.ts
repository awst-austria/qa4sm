import {ComponentFixture, TestBed} from '@angular/core/testing';

import {MetricsComponent} from './metrics.component';
import {BehaviorSubject} from 'rxjs';

describe('MetricsComponent', () => {
  let component: MetricsComponent;
  let fixture: ComponentFixture<MetricsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MetricsComponent]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MetricsComponent);
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
