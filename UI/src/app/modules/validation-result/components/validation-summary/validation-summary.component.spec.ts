import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ValidationSummaryComponent} from './validation-summary.component';

describe('ValidationSummaryComponent', () => {
  let component: ValidationSummaryComponent;
  let fixture: ComponentFixture<ValidationSummaryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ValidationSummaryComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ValidationSummaryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
