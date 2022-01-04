import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ValidationPeriodComponent} from './validation-period.component';
import {BehaviorSubject} from 'rxjs';

describe('ValidationPeriodComponent', () => {
  let component: ValidationPeriodComponent;
  let fixture: ComponentFixture<ValidationPeriodComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ValidationPeriodComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ValidationPeriodComponent);
    component = fixture.componentInstance;
    component.validationPeriodModel = {
      intervalFrom$: new BehaviorSubject(new Date()),
      intervalTo$: new BehaviorSubject(new Date())
    };
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
