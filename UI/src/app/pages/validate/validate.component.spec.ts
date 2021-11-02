import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ValidateComponent} from './validate.component';
import {DatasetService} from '../../modules/core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../modules/core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../modules/core/services/dataset/dataset-variable.service';
import {FilterService} from '../../modules/core/services/filter/filter.service';
import {ValidationRunConfigService} from './service/validation-run-config.service';
import {ToastService} from '../../modules/core/services/toast/toast.service';
import {ActivatedRoute, Router} from '@angular/router';
import {of} from 'rxjs';
import {ModalWindowService} from '../../modules/core/services/global/modal-window.service';

describe('ValidateComponent', () => {
  let component: ValidateComponent;
  let fixture: ComponentFixture<ValidateComponent>;

  beforeEach(async () => {
    const datasetServiceSpy = jasmine.createSpyObj('DatasetService',
      [
        'getDatasetById',
        'getAllDatasets'
      ]);
    const versionServiceSpy = jasmine.createSpyObj('DatasetVersionService',
      [
        'getVersionById',
        'getVersionsByDataset',
      ]);
    const variableServiceSpy = jasmine.createSpyObj('DatasetVariableService',
      [
        'getVariableById',
        'getVariablesByDataset'
      ]);
    const filterServiceSpy = jasmine.createSpyObj('FilterService', ['getFiltersByDatasetId']);
    const validationConfigServiceSpy = jasmine.createSpyObj('ValidationRunConfigService',
      [
        'getValidationConfig',
      'startValidation'
      ]);
    const toastServiceSpy = jasmine.createSpyObj('ToastService',
      [
        'showErrorWithHeader',
        'showSuccessWithHeader'
      ]);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    const routeSpy = jasmine.createSpyObj('ActivatedRoute',
      [],
      {
        queryParams: of('')
      });
    const modalWindowServiceSpy = jasmine.createSpyObj('ModalWindowService',
      {
        watch: of('open'),
        open: undefined
      });
    await TestBed.configureTestingModule({
      declarations: [ValidateComponent],
      providers: [
        {provide: DatasetService, useValue: datasetServiceSpy},
        {provide: DatasetVersionService, useValue: versionServiceSpy},
        {provide: DatasetVariableService, useValue: variableServiceSpy},
        {provide: FilterService, useValue: filterServiceSpy},
        {provide: ValidationRunConfigService, useValue: validationConfigServiceSpy},
        {provide: ToastService, useValue: toastServiceSpy},
        {provide: Router, useValue: routerSpy},
        {provide: ActivatedRoute, useValue: routeSpy},
        {provide: ModalWindowService, useValue: modalWindowServiceSpy},
      ]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ValidateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  // it('should create', () => {
  //   expect(component).toBeTruthy();
  // });
});
