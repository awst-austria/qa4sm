import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {environment} from '../../../../environments/environment';
import {UserDataFileDto} from './user-data-file.dto';

const urlPrefix = environment.API_URL + 'api';
const uploadUserDataUrl: string = urlPrefix + '/upload-user-data';
const userDataListUrl: string = urlPrefix + '/get-list-of-user-data-files';
// const validateUserDataUrl: string = urlPrefix + '/validate-user-data';

const csrfToken = '{{csrf_token}}';
const headers = new HttpHeaders({'X-CSRFToken': csrfToken});

@Injectable({
  providedIn: 'root'
})
export class UserDatasetsService {

  constructor(private httpClient: HttpClient) { }

  userFileUpload(name, file, metadata): Observable<any> {
    const formData = new FormData();
    formData.append(name, file, file.name);
    const uploadUrl = uploadUserDataUrl  + '/' + file.name + '/';
    return this.httpClient.post(uploadUrl, {formData, metadata}, {headers});
  }

  getUserDataList(): Observable<UserDataFileDto[]>{
    return this.httpClient.get<UserDataFileDto[]>(userDataListUrl);
  }

  // userFileValidate(name, file, filename): Observable<any> {
  //   const formData = new FormData();
  //   formData.append(name, file, filename);
  //   const validateUserDataUrlWithFileName = validateUserDataUrl + '/' + file.name + '/';
  //   return this.httpClient.put(validateUserDataUrlWithFileName, {file: formData.getAll(name)});
  // }

}
