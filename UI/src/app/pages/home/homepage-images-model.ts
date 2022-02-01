import {PlotDto} from '../../modules/core/services/global/plot.dto';
import {Observable} from 'rxjs';

export class HomepageImagesModel{
  constructor(public plot: Observable<PlotDto>,
              public link: string,
              public description: string) {
  }
}
