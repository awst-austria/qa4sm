import {ComponentFixture, TestBed} from '@angular/core/testing';

import {SummaryStatisticsComponent} from './summary-statistics.component';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';

describe('SummaryStatisticsComponent', () => {
  let component: SummaryStatisticsComponent;
  let fixture: ComponentFixture<SummaryStatisticsComponent>;

  beforeEach(async () => {
    const validationServiceSpy = jasmine.createSpyObj('ValidationrunService',
      [
        'getSummaryStatistics',
        'downloadSummaryStatisticsCsv'
      ]);
    const datasetServiceSpy = jasmine.createSpyObj('DatasetService', ['getDatasetById']);
    const datasetVersionServiceSpy = jasmine.createSpyObj('DatasetVersionService', ['getVersionById']);
    const datasetVariableServiceSpy = jasmine.createSpyObj('DatasetVariableService', ['getVariableById']);

    await TestBed.configureTestingModule({
      declarations: [SummaryStatisticsComponent],
      providers: [
        {provide: ValidationrunService, useValue: validationServiceSpy},
        {provide: DatasetService, useValue: datasetServiceSpy},
        {provide: DatasetVersionService, useValue: datasetVersionServiceSpy},
        {provide: DatasetVariableService, useValue: datasetVariableServiceSpy}
      ]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SummaryStatisticsComponent);
    component = fixture.componentInstance;
    component.validationRun = {
      temporal_reference_configuration: 1,
      dataset_configurations: [1, 2],
      scaling_reference_configuration: 1,
      temporal_matching: 12,
      bootstrap_tcol_cis: false,
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
      spatial_reference_configuration: 1,
      scaling_method: 'mean_std',
      scaling_ref: 1,
      start_time: new Date('2021-10-05T12:53:27.156239Z'),
      tcol: false,
      total_points: 0,
      user: 1,
    };
    component.configs = [
      // reference configuration
      {
        id: 1,
        validation: '',
        dataset: 1,
        version: 1,
        variable: 1,
        filters: [1],
        parametrised_filters: [],
        parametrisedfilter_set: [],
        is_scaling_reference: true,
        is_spatial_reference: true,
        is_temporal_reference: true
      },
      // non reference one
      {
        id: 2,
        validation: '',
        dataset: 2,
        version: 2,
        variable: 2,
        filters: [1, 2],
        parametrised_filters: [],
        parametrisedfilter_set: [],
        is_scaling_reference: false,
        is_spatial_reference: false,
        is_temporal_reference: false
      }
    ];
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
