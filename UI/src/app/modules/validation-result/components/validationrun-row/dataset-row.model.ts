import {DatasetDto} from '../../../dataset/services/dataset.dto';
import {DatasetVersionDto} from '../../../dataset/services/dataset-version.dto';
import {DatasetVariableDto} from '../../../dataset/services/dataset-variable.dto';

export class DatasetRowModel{
  constructor(public selectedDataset: DatasetDto,
              public selectedVersion: DatasetVersionDto,
              public selectedVariable: DatasetVariableDto) {
  }
}
