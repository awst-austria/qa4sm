import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ExistingValidationComponent} from './existing-validation.component';

describe('ExistingValidationComponent', () => {
  let component: ExistingValidationComponent;
  let fixture: ComponentFixture<ExistingValidationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExistingValidationComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExistingValidationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
