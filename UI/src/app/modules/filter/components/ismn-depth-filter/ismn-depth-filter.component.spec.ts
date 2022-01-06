import {ComponentFixture, TestBed} from '@angular/core/testing';

import {IsmnDepthFilterComponent} from './ismn-depth-filter.component';

describe('IsmnDepthFilterComponent', () => {
  let component: IsmnDepthFilterComponent;
  let fixture: ComponentFixture<IsmnDepthFilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [IsmnDepthFilterComponent]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(IsmnDepthFilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
