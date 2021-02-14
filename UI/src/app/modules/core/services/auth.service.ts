import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private API_URL = environment.API_URL;

  private testUrl = this.API_URL + 'api/path_test/nyaloka/';

  constructor(private httpClient: HttpClient) {
  }

  login() {

  }

  logout() {

  }

  test() {

    // this.httpClient.get(this.testUrl).subscribe(cucc => console.log(cucc));
    this.httpClient.post(this.testUrl,'') .subscribe(cucc => console.log(cucc));
  }

  isAuthenticated(): boolean {
    return true;
  }
}
