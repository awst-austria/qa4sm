import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {SettingsDto} from './settings.dto';
import {Observable, of} from 'rxjs';
import {environment} from '../../../../../environments/environment';
import {catchError, shareReplay} from 'rxjs/operators';
import {DataCache} from '../../tools/DataCache';

const settingsURL: string = environment.API_URL + 'api/settings';
const CACHE_KEY_ALL_SETTINGS = -1;

@Injectable({
  providedIn: 'root'
})
export class SettingsService {

  arrayRequestCache = new DataCache<Observable<SettingsDto[]>>(5);
  fixedSettings = [{
    id: 0,
    maintenance_mode: true,
    potential_maintenance: false,
    news: 'Sorry, something went wrong and we could not fetch news.',
    potential_maintenance_description: '',
    sum_link: 'https://qa4sm.eu/api/user-manual',
    feed_link: 'https://qa4sm.eu/ui/**'
  }]

  constructor(private httpClient: HttpClient){
  }

  getAllSettings(): Observable<SettingsDto[]> {
    if (this.arrayRequestCache.isCached(CACHE_KEY_ALL_SETTINGS)) {
      return this.arrayRequestCache.get(CACHE_KEY_ALL_SETTINGS);
    } else {
      const settings$ = this.httpClient.get<SettingsDto[]>(settingsURL)
        .pipe(
          shareReplay(),
          catchError(() => of(this.fixedSettings))
        );
      this.arrayRequestCache.push(CACHE_KEY_ALL_SETTINGS, settings$);
      return settings$;
    }
  }
}
