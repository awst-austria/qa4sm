import {ComponentFixture, TestBed} from '@angular/core/testing';

import {DatasetInfoComponent} from './dataset-info.component';
import {DatasetService} from '../../modules/core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../modules/core/services/dataset/dataset-version.service';
import {FilterService} from '../../modules/core/services/filter/filter.service';
import {DatasetDto} from '../../modules/core/services/dataset/dataset.dto';
import {of} from 'rxjs';
import {DatasetVersionDto} from '../../modules/core/services/dataset/dataset-version.dto';
import {FilterDto} from '../../modules/core/services/filter/filter.dto';

describe('DatasetInfoComponent', () => {
  let component: DatasetInfoComponent;
  let fixture: ComponentFixture<DatasetInfoComponent>;
  let getAllDatasetsSpy: jasmine.Spy;
  let getAllDatasetVersionsSpy: jasmine.Spy;
  let getAllFiltersSpy: jasmine.Spy;
  let testDatasets: DatasetDto[];
  let testVersions: DatasetVersionDto[];
  let testFilters: FilterDto[];

  beforeEach(async () => {
    const datasetService = jasmine.createSpyObj('DatasetService', ['getAllDatasets']);
    const datasetVersionService = jasmine.createSpyObj('DatasetVersionService', ['getAllVersions']);
    const filterService = jasmine.createSpyObj('FilterService', ['getAllFilters']);

    // the first defined dataset has id=2 and the second one id=1, this is done on purpose, because I test also sorting
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
        is_spatial_reference: true,
        versions: [3, 4],
        variables: [2],
        filters: [1],
        not_as_reference: false,
        user: null
      },
      {
        id: 1,
        short_name: 'C3S_combined',
        pretty_name: 'C3S SM combined',
        help_text: 'C3S long-term data record',
        storage_path: 'testdata/input_data/C3S_combined',
        detailed_description: '',
        source_reference: '',
        citation: '',
        is_spatial_reference: false,
        versions: [1, 2],
        variables: [1],
        filters: [1, 2],
        not_as_reference: false,
        user: null
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
    testFilters = [
      {
        id: 1,
        name: 'FIL_ALL_VALID_RANGE',
        description: 'Variable in valid geophysical range',
        help_text: 'Compared variable is checked for NaNs and invalid values.',
        parameterised: false,
        dialog_name: null,
        default_parameter: null,
        to_include: null,
        to_exclude: null,
        default_set_active: true,
        readonly: false,
      },
      {
        id: 2,
        name: 'FIL_C3S_FLAG_0',
        description: 'Data with no inconsistencies detected (flag = 0)',
        help_text: 'Data flag = 0 indicates good data, no inconsistencies detected.',
        parameterised: false,
        dialog_name: null,
        default_parameter: null,
        to_include: '4,5',
        to_exclude: null,
        default_set_active: true,
        readonly: false,
      },

    ];

    getAllDatasetsSpy = datasetService.getAllDatasets.and.returnValue(of(testDatasets));
    getAllDatasetVersionsSpy = datasetVersionService.getAllVersions.and.returnValue(of(testVersions));
    getAllFiltersSpy = filterService.getAllFilters.and.returnValue(of(testFilters));

    await TestBed.configureTestingModule({
      declarations: [DatasetInfoComponent],
      providers: [
        {provide: DatasetService, useValue: datasetService},
        {provide: DatasetVersionService, useValue: datasetVersionService},
        {provide: FilterService, useValue: filterService}
      ],
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DatasetInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should get all datasets', () => {
    expect(getAllDatasetsSpy.calls.any()).toBe(true);
  });

  it('should get all versions', () => {
    expect(getAllDatasetVersionsSpy.calls.any()).toBe(true);
  });

  it('should get all filters', () => {
    expect(getAllFiltersSpy.calls.any()).toBe(true);
  });

  describe('should combine datasets, filters and versions to one datasetInfo variable', () => {
    it('should combine datasets and versions', () => {
      component.ngOnInit();
      component.datasetInfo$.subscribe(data => {
        // each dataset has two versions assigned
        expect(data[0].versions.length).toEqual(2);
        expect(data[1].versions.length).toEqual(2);

        // but now, instead of numbers there should be names taken:
        expect(data[0].versions[0]).toBe(testVersions.find(version => version.id === 1).pretty_name);
        expect(data[0].versions[1]).toBe(testVersions.find(version => version.id === 2).pretty_name);

        expect(data[1].versions[0]).toBe(testVersions.find(version => version.id === 3).pretty_name);
        expect(data[1].versions[1]).toBe(testVersions.find(version => version.id === 4).pretty_name);

        //  also, help text and time range should be merged:
        expect(data[0].versionsHelpText[0]).toBe(testVersions.find(version => version.id === 1).help_text);
        expect(data[0].versionsHelpText[1]).toBe(testVersions.find(version => version.id === 2).help_text);

        expect(data[0].versionsStart[0]).toBe(testVersions.find(version => version.id === 1).time_range_start);
        expect(data[0].versionsStart[1]).toBe(testVersions.find(version => version.id === 2).time_range_start);
        expect(data[0].versionsEnd[0]).toBe(testVersions.find(version => version.id === 1).time_range_end);
        expect(data[0].versionsEnd[1]).toBe(testVersions.find(version => version.id === 2).time_range_end);

        expect(data[1].versionsHelpText[0]).toBe(testVersions.find(version => version.id === 3).help_text);
        expect(data[1].versionsHelpText[1]).toBe(testVersions.find(version => version.id === 4).help_text);

        expect(data[1].versionsStart[0]).toBe(testVersions.find(version => version.id === 3).time_range_start);
        expect(data[1].versionsStart[1]).toBe(testVersions.find(version => version.id === 4).time_range_start);
        expect(data[1].versionsEnd[0]).toBe(testVersions.find(version => version.id === 3).time_range_end);
        expect(data[1].versionsEnd[1]).toBe(testVersions.find(version => version.id === 4).time_range_end);

      });
    });
    it('should combine datasets and filters', () => {
      component.ngOnInit();
      component.datasetInfo$.subscribe(data => {
        // each dataset has two versions assigned
        expect(data[0].filters.length).toEqual(2);
        expect(data[1].filters.length).toEqual(1);


        expect(data[0].filtersHelpText[0]).toBe(testFilters.find(filter => filter.id === 1).help_text);
        expect(data[0].filtersHelpText[1]).toBe(testFilters.find(filter => filter.id === 2).help_text);
        expect(data[1].filtersHelpText[0]).toBe(testFilters.find(filter => filter.id === 1).help_text);

      });
    });
  });

});
