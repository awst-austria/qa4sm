import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Observable} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private heroesUrl = 'api/heroes';

  constructor(private http: HttpClient) {
  }

  getHeroes(): Observable<UserDTO[]> {
    return this.http.get<UserDTO[]>(this.heroesUrl);
  }
}

interface UserDTO {
  userName: string;
  email: string;
}
