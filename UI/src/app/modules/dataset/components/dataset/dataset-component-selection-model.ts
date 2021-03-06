import {DatasetDto} from '../../../core/services/dataset/dataset.dto';
import {DatasetVersionDto} from '../../../core/services/dataset/dataset-version.dto';
import {DatasetVariableDto} from '../../../core/services/dataset/dataset-variable.dto';

export class DatasetComponentSelectionModel {
  constructor(public selectedDataset: DatasetDto,
              public selectedVersion: DatasetVersionDto,
              public selectedVariable: DatasetVariableDto) {
  }
}
