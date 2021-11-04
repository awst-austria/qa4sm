import {ComponentFixture, TestBed} from '@angular/core/testing';

import {SpatialSubsetComponent} from './spatial-subset.component';
import {BehaviorSubject} from 'rxjs';

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
    component.subsetModel = {
      maxLat$: new BehaviorSubject(null),
      maxLon$: new BehaviorSubject(null),
      minLat$: new BehaviorSubject(null),
      minLon$: new BehaviorSubject(null),
      limited$: new BehaviorSubject(false)
    };
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
