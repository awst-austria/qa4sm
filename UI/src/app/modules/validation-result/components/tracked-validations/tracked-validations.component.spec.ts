import {ComponentFixture, TestBed} from '@angular/core/testing';

import {TrackedValidationsComponent} from './tracked-validations.component';

describe('TrackedValidationsComponent', () => {
  let component: TrackedValidationsComponent;
  let fixture: ComponentFixture<TrackedValidationsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TrackedValidationsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TrackedValidationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
