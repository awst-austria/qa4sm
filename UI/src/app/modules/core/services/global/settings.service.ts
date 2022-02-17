import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {SettingsDto} from './settings.dto';
import {Observable} from 'rxjs';
import {environment} from '../../../../../environments/environment';
import {shareReplay} from 'rxjs/operators';
import {DataCache} from '../../tools/DataCache';

const settingsURL: string = environment.API_URL + 'api/settings';
const CACHE_KEY_ALL_SETTINGS = -1;

@Injectable({
  providedIn: 'root'
})
export class SettingsService {

  arrayRequestCache = new DataCache<Observable<SettingsDto[]>>(5);

  constructor(private httpClient: HttpClient) {
  }

  getAllSettings(): Observable<SettingsDto[]> {
    if (this.arrayRequestCache.isCached(CACHE_KEY_ALL_SETTINGS)) {
      return this.arrayRequestCache.get(CACHE_KEY_ALL_SETTINGS);
    } else {
      const settings$ = this.httpClient.get<SettingsDto[]>(settingsURL).pipe(shareReplay());
      this.arrayRequestCache.push(CACHE_KEY_ALL_SETTINGS, settings$);
      return settings$;
    }
  }
}
