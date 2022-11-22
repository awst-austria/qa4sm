import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ValidationReferenceComponent} from './validation-reference.component';

describe('ValidationReferenceComponent', () => {
  let component: ValidationReferenceComponent;
  let fixture: ComponentFixture<ValidationReferenceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ValidationReferenceComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ValidationReferenceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
