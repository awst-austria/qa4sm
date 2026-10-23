import {ComponentFixture, TestBed} from '@angular/core/testing';

import {IsmnTolerancesFilterComponent} from './ismn-tolerances-filter.component';

describe('IsmnTolerancesFilterComponent', () => {
  let component: IsmnTolerancesFilterComponent;
  let fixture: ComponentFixture<IsmnTolerancesFilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [IsmnTolerancesFilterComponent]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(IsmnTolerancesFilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
