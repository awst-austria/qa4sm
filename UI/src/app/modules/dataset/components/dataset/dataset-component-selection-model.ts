import {DatasetDto} from '../../services/dataset.dto';
import {DatasetVersionDto} from '../../services/dataset-version.dto';
import {DatasetVariableDto} from '../../services/dataset-variable.dto';

export class DatasetComponentSelectionModel {
  constructor(public selectedDataset:DatasetDto,
              public selectedVersion:DatasetVersionDto,
              public selectedVariable:DatasetVariableDto) {
  }
}
