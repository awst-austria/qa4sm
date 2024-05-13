import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {Observable} from 'rxjs';
import {catchError, shareReplay} from 'rxjs/operators';
import {DataCache} from '../../tools/DataCache';
import {IsmnNetworkDto} from './ismn-network.dto';
import {HttpErrorService} from '../global/http-error.service';

const ismnNetworkUrl: string = environment.API_URL + 'api/ismn-network';

@Injectable({
  providedIn: 'root'
})
export class IsmnNetworkService {

  requestCache = new DataCache<Observable<IsmnNetworkDto[]>>(5);

  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService) {
  }


  getNetworksByDatasetVersionId(datasetVersionId: number): Observable<IsmnNetworkDto[]> {
    if (this.requestCache.isCached(datasetVersionId)) {
      return this.requestCache.get(datasetVersionId);
    } else {
      let params = new HttpParams().set('id', String(datasetVersionId));
      let networks$ =
        this.httpClient.get<IsmnNetworkDto[]>(ismnNetworkUrl, {params: params})
          .pipe(
            shareReplay(),
            catchError(err => this.httpError.handleError(err))
          );
      this.requestCache.push(datasetVersionId, networks$);
      return networks$;
    }
  }
}
