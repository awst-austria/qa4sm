import {DatasetDto} from '../../../core/services/dataset/dataset.dto';
import {DatasetVersionDto} from '../../../core/services/dataset/dataset-version.dto';
import {DatasetVariableDto} from '../../../core/services/dataset/dataset-variable.dto';
import {Observable} from 'rxjs';
import {FilterDto} from '../../../core/services/filter/filter.dto';

export class DatasetSummaryModel {
  constructor(public dataset$?: Observable<DatasetDto>,
              public datasetVersion$?: Observable<DatasetVersionDto>,
              public datasetVariable$?: Observable<DatasetVariableDto>,
              public datasetFilters$?: FilterDto[]) {
  }
}
