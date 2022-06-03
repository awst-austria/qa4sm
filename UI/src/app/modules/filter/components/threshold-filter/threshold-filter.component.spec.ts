import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ThresholdFilterComponent } from './threshold-filter.component';

describe('ParamtericFilterComponent', () => {
  let component: ThresholdFilterComponent;
  let fixture: ComponentFixture<ThresholdFilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ThresholdFilterComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ThresholdFilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
