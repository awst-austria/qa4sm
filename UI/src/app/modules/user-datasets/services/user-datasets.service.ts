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
const userDataTestUrl: string = urlPrefix + '/test-user-dataset';
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

  userFileUpload(name, file): Observable<any> {
    const formData = new FormData();
    formData.append(name, file, file.name);
    const uploadUrl = uploadUserDataUrl  + '/' + file.name + '/';
    return this.httpClient.post(uploadUrl, formData.get(name), {headers, observe: 'body', responseType: 'json'});
  }

  getUserDataList(): Observable<UserDataFileDto[]>{
    return this.httpClient.get<UserDataFileDto[]>(userDataListUrl);
  }

  deleteUserData(dataFileId: string): Observable<any>{
    const deleteUrl = userDataDeleteUrl + '/' + dataFileId + '/';
    return this.httpClient.delete(deleteUrl, {headers});
  }

  sendMetadata(metadataForm: any, fileId: string): Observable<any> {
    const metadataUrl = userDataMetadataUrl + '/' + fileId + '/';
    return this.httpClient.post(metadataUrl, metadataForm, {observe: 'body', responseType: 'json'});
  }

  testDataset(dataFileId: string): Observable<any>{
    const testUrl = userDataTestUrl + '/' + dataFileId + '/';
    return this.httpClient.get(testUrl);
  }

  // userFileValidate(name, file, filename): Observable<any> {
  //   const formData = new FormData();
  //   formData.append(name, file, filename);
  //   const validateUserDataUrlWithFileName = validateUserDataUrl + '/' + file.name + '/';
  //   return this.httpClient.put(validateUserDataUrlWithFileName, {file: formData.getAll(name)});
  // }

}
