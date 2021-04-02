import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ValidationrunRowComponent } from './validationrun-row.component';

describe('ValidationrunRowComponent', () => {
  let component: ValidationrunRowComponent;
  let fixture: ComponentFixture<ValidationrunRowComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ValidationrunRowComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ValidationrunRowComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
