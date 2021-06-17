import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {Observable} from 'rxjs';
import {shareReplay} from 'rxjs/operators';
import {DataCache} from '../../tools/DataCache';
import {IsmnNetworkDto} from './ismn-network.dto';

const ismnNetworkUrl: string = environment.API_URL + 'api/ismn-network';

@Injectable({
  providedIn: 'root'
})
export class IsmnNetworkService {

  requestCache = new DataCache<Observable<IsmnNetworkDto[]>>(5);

  constructor(private httpClient: HttpClient) {
  }


  getNetworksByDatasetVersionId(datasetVersionId: number): Observable<IsmnNetworkDto[]> {
    if (this.requestCache.isCached(datasetVersionId)) {
      return this.requestCache.get(datasetVersionId);
    } else {
      let params = new HttpParams().set('id', String(datasetVersionId));
      let networks$ = this.httpClient.get<IsmnNetworkDto[]>(ismnNetworkUrl, {params: params}).pipe(shareReplay());
      this.requestCache.push(datasetVersionId, networks$);
      return networks$;
    }
  }
}
