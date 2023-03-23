import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ValidationrunRowComponent} from './validationrun-row.component';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';

describe('ValidationrunRowComponent', () => {
  let component: ValidationrunRowComponent;
  let fixture: ComponentFixture<ValidationrunRowComponent>;
  let globalParamServiceStub: Partial<GlobalParamsService>;
  let globalService: GlobalParamsService;

  beforeEach(async () => {
    globalParamServiceStub = {
      globalContext: {
        admin_mail: '',
        doi_prefix: '100/11010.11',
        site_url: '',
        app_version: '1.6.0',
        expiry_period: '',
        warning_period: '',
      }
    };
    const datasetConfigServiceSpy = jasmine.createSpyObj('DatasetConfigurationService', ['getConfigByValidationrun']);
    const datasetServiceSpy = jasmine.createSpyObj('DatasetService', ['getAllDatasets']);
    const datasetVersionServiceSpy = jasmine.createSpyObj('DatasetVersionService', ['getAllVersions']);
    const datasetVariableServiceSpy = jasmine.createSpyObj('DatasetVariableService', ['getAllVariables']);
    const validationServiceSpy = jasmine.createSpyObj('ValidationrunService',
      [
        'saveResultsName',
        'refreshComponent',
        'getCopiedRunRecord'
      ]);

    await TestBed.configureTestingModule({
      declarations: [ValidationrunRowComponent],
      providers: [{provide: DatasetConfigurationService, useValue: datasetConfigServiceSpy},
        {provide: DatasetService, useValue: datasetServiceSpy},
        {provide: DatasetVersionService, useValue: datasetVersionServiceSpy},
        {provide: DatasetVariableService, useValue: datasetVariableServiceSpy},
        {provide: GlobalParamsService, useValue: globalParamServiceStub},
        {provide: ValidationrunService, useValue: validationServiceSpy}]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ValidationrunRowComponent);
    component = fixture.componentInstance;
    component.published = false;
    component.validationRun = {
        anomalies: 'none',
        anomalies_from: null,
        anomalies_to: null,
        copied_run: [],
        doi: '10030-10102/11',
        end_time: new Date('2021-10-05T12:53:27.424039Z'),
        error_points: 0,
        expiry_date: new Date('2021-12-04T12:53:27.424Z'),
        expiry_notified: false,
        id: '',
        interval_from: new Date('1978-11-01T00:00:00Z'),
        interval_to: new Date('2019-12-31T23:59:59.999999Z'),
        is_a_copy: false,
        is_archived: false,
        is_near_expiry: false,
        is_unpublished: true,
        last_extended: null,
        max_lat: 71.6,
        max_lon: 48.3,
        min_lat: 34,
        min_lon: -11.2,
        name_tag: 'second validation',
        ok_points: 0,
        output_dir_url: null,
        output_file: null,
        output_file_name: null,
        progress: 0,
        publishing_in_progress: false,
        spatial_reference_configuration: 4699,
        scaling_method: 'mean_std',
        scaling_ref: 4699,
        start_time: new Date('2021-10-05T12:53:27.156239Z'),
        tcol: false,
        total_points: 0,
        user: 1,
    };
    globalService = fixture.debugElement.injector.get(GlobalParamsService);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
