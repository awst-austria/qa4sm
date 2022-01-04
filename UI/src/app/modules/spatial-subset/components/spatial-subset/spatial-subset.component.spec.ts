import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SpatialSubsetComponent } from './spatial-subset.component';

describe('SpatialSubsetComponent', () => {
  let component: SpatialSubsetComponent;
  let fixture: ComponentFixture<SpatialSubsetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SpatialSubsetComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SpatialSubsetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
