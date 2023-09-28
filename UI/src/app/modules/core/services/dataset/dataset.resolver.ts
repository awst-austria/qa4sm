import {Injectable} from '@angular/core';
import {ActivatedRouteSnapshot, RouterStateSnapshot} from '@angular/router';
import {Observable} from 'rxjs';
import {DatasetService} from './dataset.service';
import {DatasetDto} from './dataset.dto';

@Injectable({
  providedIn: 'root'
})
export class DatasetResolver  {
  constructor(private datasetService: DatasetService) {
  }

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<DatasetDto[]> {
    const name = route.queryParamMap.get('cucc');
    return this.datasetService.getAllDatasets(true);
  }
}
