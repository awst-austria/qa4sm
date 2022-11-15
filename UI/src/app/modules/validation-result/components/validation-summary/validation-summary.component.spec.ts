import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ValidationSummaryComponent} from './validation-summary.component';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {FilterService} from '../../../core/services/filter/filter.service';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {AuthService} from '../../../core/services/auth/auth.service';
import {Router} from '@angular/router';
import {of} from 'rxjs';

describe('ValidationSummaryComponent', () => {
  let component: ValidationSummaryComponent;
  let fixture: ComponentFixture<ValidationSummaryComponent>;

  beforeEach(async () => {
    const datasetServiceSpy = jasmine.createSpyObj('DatasetService', ['getAllDatasets']);
    const datasetVersionServiceSpy = jasmine.createSpyObj('DatasetVersionService', ['getAllVersions']);
    const datasetVariableServiceSpy = jasmine.createSpyObj('DatasetVariableService', ['getAllVariables']);
    const filterServiceSpy = jasmine.createSpyObj('FilterService', ['getAllFilters', 'getAllParameterisedFilters']);
    const globalParamsService = jasmine.createSpyObj('GlobalParamsService',
      [],
      {
        globalContext: {
          admin_mail: '',
          doi_prefix: '',
          site_url: '',
          app_version: '',
          expiry_period: '',
          warning_period: '',
        }
      });
    const validationServiceSpy = jasmine.createSpyObj('ValidationrunService',
      [
        'saveResultsName',
        'getCopiedRunRecord'
      ]);
    const authServiceSpy = jasmine.createSpyObj('AuthService',
      [],
      {
        currentUser: {
          username: '',
          first_name: '',
          id: 1,
          copied_runs: [],
          email: '',
          last_name: '',
          organisation: '',
          country: '',
          orcid: ''
        }
      });
    const routerSpy =  jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      declarations: [ ValidationSummaryComponent ],
      providers: [
        {provide: DatasetService, useValue: datasetServiceSpy},
        {provide: DatasetVersionService, useValue: datasetVersionServiceSpy},
        {provide: DatasetVariableService, useValue: datasetVariableServiceSpy},
        {provide: FilterService, useValue: filterServiceSpy},
        {provide: GlobalParamsService, useValue: globalParamsService},
        {provide: ValidationrunService, useValue: validationServiceSpy},
        {provide: AuthService, useValue: authServiceSpy},
        {provide: Router, useValue: routerSpy}
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ValidationSummaryComponent);
    component = fixture.componentInstance;
    component.validationModel = {
      validationRun: of({
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
        bootstrap_tcol_cis: false
      }),
      datasetConfigs: of([])
    };
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
