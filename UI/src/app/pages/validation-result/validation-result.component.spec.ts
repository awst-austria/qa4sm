import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ValidationResultComponent} from './validation-result.component';
import {of} from 'rxjs';
import {ActivatedRoute} from '@angular/router';
import {ValidationrunService} from '../../modules/core/services/validation-run/validationrun.service';
import {DatasetConfigurationService} from '../../modules/validation-result/services/dataset-configuration.service';
import {ModalWindowService} from '../../modules/core/services/global/modal-window.service';

describe('ValidationComponent', () => {
  let component: ValidationResultComponent;
  let fixture: ComponentFixture<ValidationResultComponent>;

  beforeEach(async () => {
    const routeSpy = jasmine.createSpyObj('ActivatedRoute',
      [],
      {
        params: of('')
      });
    const validationRunServiceSpy = jasmine.createSpyObj('ValidationrunService', ['getValidationRunById']);
    const datasetConfigurationServiceSpy = jasmine.createSpyObj('DatasetConfigurationService', ['getConfigByValidationrun'])
    const modalWindowServiceSpy = jasmine.createSpyObj('ModalWindowService',
      {
        watch: of('open')
      });
    await TestBed.configureTestingModule({
      declarations: [ValidationResultComponent],
      providers: [
        {provide: ActivatedRoute, useValue: routeSpy},
        {provide: ValidationrunService, useValue: validationRunServiceSpy},
        {provide: DatasetConfigurationService, useValue: datasetConfigurationServiceSpy},
        {provide: ModalWindowService, useValue: modalWindowServiceSpy},
      ]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ValidationResultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
