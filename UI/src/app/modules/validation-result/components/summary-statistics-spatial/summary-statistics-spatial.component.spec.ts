import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SummaryStatisticsSpatialComponent } from './summary-statistics-spatial.component';

describe('SummaryStatisticsSpatialComponent', () => {
  let component: SummaryStatisticsSpatialComponent;
  let fixture: ComponentFixture<SummaryStatisticsSpatialComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SummaryStatisticsSpatialComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SummaryStatisticsSpatialComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
