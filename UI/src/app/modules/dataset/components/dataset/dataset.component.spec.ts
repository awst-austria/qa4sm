import {ComponentFixture, TestBed} from '@angular/core/testing';

import {DatasetComponent} from './dataset.component';
import {DatasetDto} from '../../../core/services/dataset/dataset.dto';
import {DatasetVersionDto} from '../../../core/services/dataset/dataset-version.dto';
import {DatasetVariableDto} from '../../../core/services/dataset/dataset-variable.dto';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {of} from 'rxjs';

describe('DatasetComponent', () => {
  let component: DatasetComponent;
  let fixture: ComponentFixture<DatasetComponent>;
  let testDatasets: DatasetDto[];
  let testVersions: DatasetVersionDto[];
  let testVariables: DatasetVariableDto[];

  let getAllDatasetsSpy: jasmine.Spy;

  beforeEach(async () => {
    const datasetService = jasmine.createSpyObj('DatasetService', ['getAllDatasets']);
    const datasetVersionService = jasmine.createSpyObj('DatasetVersionService', ['getVersionsByDataset']);
    const datasetVariableService = jasmine.createSpyObj('DatasetVariableService', ['getVariablesByDataset']);
    testDatasets = [
      {
        id: 2,
        short_name: 'SMAP',
        pretty_name: 'SMAP level 3',
        help_text: 'NASA SMAP level 3 data',
        storage_path: 'testdata/input_data/SMAP',
        detailed_description: '',
        source_reference: '',
        citation: '',
        is_only_reference: true,
        versions: [3, 4],
        variables: [2],
        filters: [1],
        not_as_reference: false
      },
      {
        id: 1,
        short_name: 'C3S',
        pretty_name: 'C3S',
        help_text: 'C3S long-term data record',
        storage_path: 'testdata/input_data/C3S',
        detailed_description: '',
        source_reference: '',
        citation: '',
        is_only_reference: false,
        versions: [1, 2],
        variables: [1],
        filters: [1, 2],
        not_as_reference: false
      },
    ];

    testVersions = [
      {
        id: 1,
        short_name: 'C3S_V201706',
        pretty_name: 'v201706',
        help_text: 'C3S from June 2017',
        geographical_range: null,
        time_range_end: new Date('2017-06-30'),
        time_range_start: new Date('1978-11-01'),
      },
      {
        id: 2,
        short_name: 'C3S_V201812',
        pretty_name: 'v201812',
        help_text: 'C3S from December 2018',
        geographical_range: null,
        time_range_end: new Date('1978-11-01'),
        time_range_start: new Date('2018-12-31'),
      },
      {
        id: 3,
        short_name: 'SMAP_V5_PM',
        pretty_name: 'v5 PM/ascending',
        help_text: '',
        geographical_range: null,
        time_range_end: new Date('2015-03-31'),
        time_range_start: new Date('2018-12-04'),
      },
      {
        id: 4,
        short_name: 'SMAP_V6_PM',
        pretty_name: 'v6 PM/ascending',
        help_text: '',
        geographical_range: null,
        time_range_end: new Date('2015-03-31'),
        time_range_start: new Date('2020-05-23'),
      }
    ];
    testVariables = [
      { id: 1,
        short_name: 'C3S_sm',
        pretty_name: 'sm',
        help_text: '',
        min_value: 0.0,
        max_value: 1.0}
    ];

    getAllDatasetsSpy = datasetService.getAllDatasets.and.returnValue(of(testDatasets));

    await TestBed.configureTestingModule({
      declarations: [DatasetComponent],
      providers: [
        {provide: DatasetService, useValue: datasetService},
        {provide: DatasetVersionService, useValue: datasetVersionService},
        {provide: DatasetVariableService, useValue: datasetVariableService},
      ]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DatasetComponent);
    component = fixture.componentInstance;
    component.removable = false;
    component.reference = false;
    component.selectionModel = {
      selectedDataset: testDatasets[0],
      selectedVersion: testVersions[0],
      selectedVariable: testVariables[0]
    };


    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
