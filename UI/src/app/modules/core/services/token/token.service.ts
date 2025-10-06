import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../../environments/environment';

export interface TokenResponse {
  token: string;
  status: 'pending' | 'approved' | 'rejected';
}

@Injectable({
  providedIn: 'root'
})
export class TokenService {
  private API_URL = environment.API_URL;

  constructor(private http: HttpClient) {}

  getToken(): Observable<TokenResponse> {
    return this.http.get<TokenResponse>(`${this.API_URL}api/get-api-token`);
  }

  requestToken(): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.API_URL}api/request-api-token`, {});
  }

}
