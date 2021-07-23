import {DatasetConfigModel} from './dataset-config-model';
import {SpatialSubsetModel} from '../../modules/spatial-subset/components/spatial-subset/spatial-subset-model';
import {ValidationPeriodModel} from '../../modules/validation-period/components/validation-period/validation-period-model';
import {MetricModel} from '../../modules/metrics/components/metric/metric-model';
import {AnomaliesModel} from '../../modules/anomalies/components/anomalies/anomalies-model';
import {ScalingModel} from '../../modules/scaling/components/scaling/scaling-model';
import {BehaviorSubject} from 'rxjs';

export class ValidationModel {
  // The reference configuration array should contain exactly one item.
  constructor(public datasetConfigurations: DatasetConfigModel[],
              public referenceConfigurations: DatasetConfigModel[],
              public spatialSubsetModel: SpatialSubsetModel,
              public validationPeriodModel: ValidationPeriodModel,
              public metrics: MetricModel[],
              public anomalies: AnomaliesModel,
              public scalingModel: ScalingModel,
              public nameTag$: BehaviorSubject<string>) {
  }
}
