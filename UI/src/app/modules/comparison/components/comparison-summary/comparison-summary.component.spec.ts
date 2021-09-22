import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ComparisonSummaryComponent } from './comparison-summary.component';

describe('ComparisonSummaryComponent', () => {
  let component: ComparisonSummaryComponent;
  let fixture: ComponentFixture<ComparisonSummaryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ComparisonSummaryComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ComparisonSummaryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
