import {Injectable} from '@angular/core';
import {BehaviorSubject, Observable} from 'rxjs';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {environment} from '../../../../environments/environment';
import {UserDataFileDto} from './user-data-file.dto';

const urlPrefix = environment.API_URL + 'api';
const uploadUserDataUrl: string = urlPrefix + '/upload-user-data';
const userDataListUrl: string = urlPrefix + '/get-list-of-user-data-files';
const userDataDeleteUrl: string = urlPrefix + '/delete-user-dataset';
const userDataMetadataUrl: string = urlPrefix + '/user-file-metadata';
// const validateUserDataUrl: string = urlPrefix + '/validate-user-data';

const csrfToken = '{{csrf_token}}';
const headers = new HttpHeaders({'X-CSRFToken': csrfToken});

@Injectable({
  providedIn: 'root'
})
export class UserDatasetsService {

  public refresh: BehaviorSubject<boolean> = new BehaviorSubject(false);
  doRefresh = this.refresh.asObservable();

  constructor(private httpClient: HttpClient) { }

  userFileUpload(name, file, fileId): Observable<any> {
    const formData = new FormData();
    formData.append(name, file, file.name);
    const uploadUrl = uploadUserDataUrl  + '/' + file.name + '/' + fileId + '/';
    return this.httpClient.post(uploadUrl, formData, {headers});
  }

  getUserDataList(): Observable<UserDataFileDto[]>{
    return this.httpClient.get<UserDataFileDto[]>(userDataListUrl);
  }

  deleteUserData(datasetId: number): Observable<any>{
    const deleteUrl = userDataDeleteUrl + '/' + datasetId + '/';
    return this.httpClient.delete(deleteUrl, {headers});
  }

  sendMetadata(metadataForm: any): Observable<any> {
    return this.httpClient.post(userDataMetadataUrl, metadataForm, {observe: 'body', responseType: 'json'});
  }

  // userFileValidate(name, file, filename): Observable<any> {
  //   const formData = new FormData();
  //   formData.append(name, file, filename);
  //   const validateUserDataUrlWithFileName = validateUserDataUrl + '/' + file.name + '/';
  //   return this.httpClient.put(validateUserDataUrlWithFileName, {file: formData.getAll(name)});
  // }

}
