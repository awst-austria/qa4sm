import {ComponentFixture, TestBed} from '@angular/core/testing';

import {DatasetInfoComponent} from './dataset-info.component';
import {DatasetService} from '../../modules/core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../modules/core/services/dataset/dataset-version.service';
import {FilterService} from '../../modules/core/services/filter/filter.service';

describe('DatasetInfoComponent', () => {
  let component: DatasetInfoComponent;
  let fixture: ComponentFixture<DatasetInfoComponent>;
  let getAllDatasetsSpy: jasmine.Spy;
  let getAllDatasetVersionsSpy: jasmine.Spy;
  let getAllFiltersSpy: jasmine.Spy;

  beforeEach(async () => {
    const datasetService = jasmine.createSpyObj('DatasetService', ['getAllDatasets']);
    const datasetVersionService = jasmine.createSpyObj('DatasetVersionService', ['getAllVersions']);
    const filterService = jasmine.createSpyObj('FilterService', ['getAllFilters']);

    await TestBed.configureTestingModule({
      declarations: [ DatasetInfoComponent ],
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
});
