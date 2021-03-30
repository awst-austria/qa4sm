import {Component, OnInit} from '@angular/core';
import {DatasetService} from '../../modules/core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../modules/core/services/dataset/dataset-version.service';
import {FilterService} from '../../modules/core/services/filter/filter.service';
import {combineLatest, Observable} from 'rxjs';
import {map} from 'rxjs/operators';

@Component({
  selector: 'qa-dataset-info',
  templateUrl: './dataset-info.component.html',
  styleUrls: ['./dataset-info.component.scss']
})
export class DatasetInfoComponent implements OnInit {

  datasetInfo$: Observable<any>;
  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private filterService: FilterService) { }

  ngOnInit(): void {
    this.updateDatasetInfo();
  }

  private updateDatasetInfo(): void{
    this.datasetInfo$ = combineLatest(
      this.datasetService.getAllDatasets(),
      this.versionService.getAllVersions(),
      this.filterService.getAllFilters()
    ).pipe(
      map(([datasets, versions, filters]) =>
        datasets.map(
          dataset =>
            ({...dataset,
              versions: dataset.versions.map(versionId => versions.find(version => version.id === versionId).pretty_name),
              versionsHelpText: dataset.versions.map(versionId => versions.find(version => version.id === versionId).help_text),
              versionsStart: dataset.versions.map(versionId => versions.find(version => version.id === versionId).time_range_start),
              versionsEnd: dataset.versions.map(versionId => versions.find(version => version.id === versionId).time_range_end),
              filters: dataset.filters.map(filterId => filters.find(filter => filter.id === filterId).description),
              filtersHelpText: dataset.filters.map(filterId => filters.find(filter => filter.id === filterId).help_text),
            })
        )
      )
    );
  }

}
