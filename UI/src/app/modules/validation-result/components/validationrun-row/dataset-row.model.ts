import {DatasetDto} from '../../../core/services/dataset/dataset.dto';
import {DatasetVersionDto} from '../../../core/services/dataset/dataset-version.dto';
import {DatasetVariableDto} from '../../../core/services/dataset/dataset-variable.dto';
import {Observable} from 'rxjs';

export class DatasetRowModel {
  constructor(public dataset$?: Observable<DatasetDto>,
              public datasetVersion$?: Observable<DatasetVersionDto>,
              public datasetVariable$?: Observable<DatasetVariableDto>,) {
  }
}
