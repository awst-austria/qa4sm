import {TestBed} from '@angular/core/testing';

import {DatasetResolver} from './dataset.resolver';
import {DatasetService} from './dataset.service';

describe('DatasetResolver', () => {
  let resolver: DatasetResolver;

  beforeEach(() => {
    const datasetServiceSpy = jasmine.createSpyObj('DatasetService', ['getAllDatasets']);
    TestBed.configureTestingModule({
      providers: [{provide: DatasetService, useValue: datasetServiceSpy}]
    });
    resolver = TestBed.inject(DatasetResolver);
  });

  it('should be created', () => {
    expect(resolver).toBeTruthy();
  });
});
