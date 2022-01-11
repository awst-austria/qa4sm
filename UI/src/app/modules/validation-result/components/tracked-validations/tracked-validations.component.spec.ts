import {ComponentFixture, TestBed} from '@angular/core/testing';

import {TrackedValidationsComponent} from './tracked-validations.component';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';

describe('TrackedValidationsComponent', () => {
  let component: TrackedValidationsComponent;
  let fixture: ComponentFixture<TrackedValidationsComponent>;

  beforeEach(async () => {
    const validationrunServiceSpy = jasmine.createSpyObj('ValidationrunService',
      ['getCustomTrackedValidations']);
    await TestBed.configureTestingModule({
      declarations: [ TrackedValidationsComponent ],
      providers: [{provide: ValidationrunService, useValue: validationrunServiceSpy}]
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
