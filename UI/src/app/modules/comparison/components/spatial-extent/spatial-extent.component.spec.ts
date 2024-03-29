import {ComponentFixture, TestBed} from '@angular/core/testing';

import {SpatialExtentComponent} from './spatial-extent.component';

describe('SpatialExtentComponent', () => {
  let component: SpatialExtentComponent;
  let fixture: ComponentFixture<SpatialExtentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SpatialExtentComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SpatialExtentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
