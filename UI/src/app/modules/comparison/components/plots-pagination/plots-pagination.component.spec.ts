import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlotsPaginationComponent } from './plots-pagination.component';

describe('PlotsPaginationComponent', () => {
  let component: PlotsPaginationComponent;
  let fixture: ComponentFixture<PlotsPaginationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PlotsPaginationComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PlotsPaginationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
