import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ValidationSelectorComponent } from './validation-selector.component';

describe('ValidationSelectorComponent', () => {
  let component: ValidationSelectorComponent;
  let fixture: ComponentFixture<ValidationSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ValidationSelectorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ValidationSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
