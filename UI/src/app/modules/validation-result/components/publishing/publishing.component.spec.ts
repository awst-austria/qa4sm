import {ComponentFixture, TestBed} from '@angular/core/testing';

import {PublishingComponent} from './publishing.component';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {FormBuilder} from '@angular/forms';

describe('PublishingComponent', () => {
  let component: PublishingComponent;
  let fixture: ComponentFixture<PublishingComponent>;

  beforeEach(async () => {
    const modalServiceSpy = jasmine.createSpyObj('ModalWindowService', ['watch', 'close', 'open']);
    const validationrunServiceSpy = jasmine.createSpyObj('ValidationrunService',
      ['publishResults', 'getPublishingFormData']);
    const formBuilderSpy = jasmine.createSpyObj('FormBuilder', ['group']);

    await TestBed.configureTestingModule({
      declarations: [ PublishingComponent ],
      providers: [
        {provide: ModalWindowService, useValue: modalServiceSpy},
        {provide: FormBuilder, useValue: formBuilderSpy},
        {provide: ValidationrunService, useValue: validationrunServiceSpy}
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PublishingComponent);
    component = fixture.componentInstance;
    component.validationId = 'f0000000-a000-b000-c000-d00000000000';
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
