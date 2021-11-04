import {ComponentFixture, TestBed} from '@angular/core/testing';

import {MetricComponent} from './metric.component';
import {BehaviorSubject} from 'rxjs';

describe('MetricComponent', () => {
  let component: MetricComponent;
  let fixture: ComponentFixture<MetricComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MetricComponent]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MetricComponent);
    component = fixture.componentInstance;
    component.metricModel = {
      description: '',
      helperText: '',
      value$: new BehaviorSubject(false),
      enabled: false,
      id: '1',
      toValidationRunMetricDto: null
    };
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
