import {ComponentFixture, TestBed} from '@angular/core/testing';

import {IntraAnnualMetricsComponent} from './intra-annual-metrics.component';

describe('IntraAnnualMetricsComponent', () => {
  let component: IntraAnnualMetricsComponent;
  let fixture: ComponentFixture<IntraAnnualMetricsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IntraAnnualMetricsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(IntraAnnualMetricsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
