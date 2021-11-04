import {ComponentFixture, TestBed} from '@angular/core/testing';

import {PublishingComponent} from './publishing.component';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {ReactiveFormsModule} from '@angular/forms';
import {of} from 'rxjs';

describe('PublishingComponent', () => {
  let component: PublishingComponent;
  let fixture: ComponentFixture<PublishingComponent>;

  beforeEach(async () => {
    const testPublishingForm = {
      title: '',
      description: '',
      keywords: '',
      name: '',
      affiliation: '',
      orcid: ''
    };
    const modalServiceSpy = jasmine.createSpyObj('ModalWindowService', ['watch', 'close', 'open']);
    const validationrunServiceSpy = jasmine.createSpyObj('ValidationrunService',
      {
        publishResults: undefined,
        getPublishingFormData: of(testPublishingForm),
      });

    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule],
      declarations: [PublishingComponent],
      providers: [
        {provide: ModalWindowService, useValue: modalServiceSpy},
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
