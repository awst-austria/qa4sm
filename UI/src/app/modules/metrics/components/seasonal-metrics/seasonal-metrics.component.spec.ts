import {ComponentFixture, TestBed} from '@angular/core/testing';

import {SeasonalMetricsComponent} from './seasonal-metrics.component';

describe('SeasonalMetricsComponent', () => {
  let component: SeasonalMetricsComponent;
  let fixture: ComponentFixture<SeasonalMetricsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SeasonalMetricsComponent]
    });
    fixture = TestBed.createComponent(SeasonalMetricsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
