import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ExistingValidationComponent} from './existing-validation.component';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';
import {Router} from '@angular/router';

describe('ExistingValidationComponent', () => {
  let component: ExistingValidationComponent;
  let fixture: ComponentFixture<ExistingValidationComponent>;

  beforeEach(async () => {
    const validationServiceSpy = jasmine.createSpyObj('ValidationrunService', ['getValidationRunById']);
    const modalServiceSpy = jasmine.createSpyObj('ModalWindowService', ['watch', 'close']);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      declarations: [ ExistingValidationComponent ],
      providers: [
        {provide: ValidationrunService, useValue: validationServiceSpy},
        {provide: ModalWindowService, useValue: modalServiceSpy},
        {provide: Router, useValue: routerSpy}]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExistingValidationComponent);
    component = fixture.componentInstance;
    component.isThereValidation = {
       is_there_validation: false,
       val_id: '',
       belongs_to_user: false,
       is_published: false
    };
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
