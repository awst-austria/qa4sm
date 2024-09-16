import {ComponentFixture, TestBed} from '@angular/core/testing';

import {InterAnnualMetricsComponent} from './inter-annual-metrics.component';

describe('InterAnnualMetricsComponent', () => {
  let component: InterAnnualMetricsComponent;
  let fixture: ComponentFixture<InterAnnualMetricsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InterAnnualMetricsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InterAnnualMetricsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
