import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ValidationPeriodComponent } from './validation-period.component';

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
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
