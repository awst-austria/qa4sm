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
  toggleOption = [];
  allSelected: boolean;

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private filterService: FilterService) {
  }

  ngOnInit(): void {
    this.updateDatasetInfo();
    this.sort();
    this.toggleOption = [
      {label: 'Expand all',
      value: true},
      {label: 'Close all',
      value: false}
    ]
  }

  private updateDatasetInfo(): void {
    this.datasetInfo$ = combineLatest(
      this.datasetService.getAllDatasets(),
      this.versionService.getAllVersions(),
      this.filterService.getAllFilters()
    ).pipe(
      map(([datasets, versions, filters]) =>
        datasets.map(
          dataset => {
            const datasetVersions = dataset.versions.map(versionId =>
              versions.find(version => version.id === versionId)
            );
            return {
              ...dataset,
              versions: datasetVersions.map(version => version.pretty_name),
              versionsHelpText: datasetVersions.map(version => version.help_text),
              versionsStart: datasetVersions.map(version => version.time_range_start),
              versionsEnd: datasetVersions.map(version => version.time_range_end),
              versionsFilters: datasetVersions.map(version => version.filters),
              filtersIds: this.getDistincFilters(datasetVersions.flatMap(version => version.filters.map(filterId =>
                filters.find(filter => filter.id === filterId).id
              ))),
              filtersDescription: this.getDistincFilters(datasetVersions.flatMap(version => version.filters.map(filterId =>
                filters.find(filter => filter.id === filterId).description
              ))),
              filtersHelpText: this.getDistincFilters(datasetVersions.flatMap(version => version.filters.map(filterId =>
                filters.find(filter => filter.id === filterId).help_text
              ))),
            }
          }
        )
      )
    );
  }

  sort(): void {
    this.datasetInfo$ = this.datasetInfo$.pipe(map((data) => {
      data.sort((a, b) => {
        return a.id < b.id ? -1 : 1;
      });
      return data;
    }));
  }

  getDistincFilters(filters, t = {}): any {
    return filters.filter(e => !(t[e] = e in t));
  }

  getPositionsOfElementsInList(entireList: any[], partialList: any[]): number[] {
    return partialList.map(itemB => entireList.indexOf(itemB) + 1);
  }

  protected readonly String = String;
}
