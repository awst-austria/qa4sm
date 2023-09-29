import {Injectable} from '@angular/core';
import {BehaviorSubject, Observable} from 'rxjs';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {environment} from '../../../../environments/environment';
import {UserDataFileDto} from './user-data-file.dto';
import {DataManagementGroupsDto} from './data-management-groups.dto';


const urlPrefix = environment.API_URL + 'api';
const uploadUserDataUrl: string = urlPrefix + '/upload-user-data';
const userDataListUrl: string = urlPrefix + '/get-list-of-user-data-files';
const userDataDeleteUrl: string = urlPrefix + '/delete-entire-dataset';
const userDeleteFileOnlyUrl: string = urlPrefix + '/delete-only-datafile';
const updateMetadataUrl: string = urlPrefix + '/update-metadata';
const userDataFileUrl: string = urlPrefix + '/get-user-file-by-id';
const dataManagementGroupsUrl: string = urlPrefix + '/data-management-groups';
const manageDataInGroupUrl: string = urlPrefix + '/manage-data-in-management-group';


const csrfToken = '{{csrf_token}}';
const headers = new HttpHeaders({'X-CSRFToken': csrfToken});

@Injectable({
  providedIn: 'root'
})
export class UserDatasetsService {

  public refresh: BehaviorSubject<boolean> = new BehaviorSubject(false);
  doRefresh = this.refresh.asObservable();

  public openSharingDataWindow: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false)
  doOpenSharingDataWindow = this.openSharingDataWindow.asObservable();

  constructor(private httpClient: HttpClient) { }

  userFileUpload(name, file, fileName, metadata): Observable<any> {
    const formData = new FormData();
    formData.append(name, file, fileName);
    const uploadUrl = uploadUserDataUrl  + '/' + fileName + '/';
    const fileHeaders = new HttpHeaders({'X-CSRFToken': csrfToken, fileMetadata: JSON.stringify(metadata)});
    return this.httpClient.post(uploadUrl, formData.get(name),
      {headers: fileHeaders, reportProgress: true, observe: 'events', responseType: 'json'});
  }

  getUserDataList(): Observable<UserDataFileDto[]>{
    return this.httpClient.get<UserDataFileDto[]>(userDataListUrl);
  }

  getUserDataFileById(fileId: string): Observable<UserDataFileDto>{
    const userDataFileUrlWithId = userDataFileUrl + '/'  + fileId + '/';
    return this.httpClient.get<UserDataFileDto>(userDataFileUrlWithId);
  }

  deleteUserData(dataFileId: string): Observable<any>{
    const deleteUrl = userDataDeleteUrl + '/' + dataFileId + '/';
    return this.httpClient.delete(deleteUrl, {headers});
  }

  deleteUserDataFileOnly(dataFileId: string): Observable<any>{
    const deleteUrl = userDeleteFileOnlyUrl + '/' + dataFileId + '/';
    return this.httpClient.delete(deleteUrl, {headers});
  }


  updateMetadata(fieldName: string, fieldValue: string, dataFileId: string): Observable<any>{
    const updateUrl = updateMetadataUrl + '/' + dataFileId + '/';
    return this.httpClient.put(updateUrl, {field_name: fieldName, field_value: fieldValue});
  }

  getDataManagementGroups(ids=[]): Observable<DataManagementGroupsDto[]>{
    let params = new HttpParams();
    ids.forEach((id) => {
      params = params.append('id', id)
    });
    return this.httpClient.get<DataManagementGroupsDto[]>(dataManagementGroupsUrl, {params})
  }

  manageDataInManagementGroup(group_id: number, data_id: string, action: string): Observable<any>{
    return this.httpClient.put<any>(manageDataInGroupUrl, {group_id, data_id, action})
  }

  getTheSizeInProperUnits(sizeInBites): string {
    let properSize;
    let units;
    const coeff = Math.pow(10, 6);
    if (sizeInBites < coeff) {
      properSize = sizeInBites / Math.pow(10, 3);
      units = 'kB';
    } else if (sizeInBites >= coeff && sizeInBites < coeff * 1000) {
      properSize = sizeInBites / coeff;
      units = 'MB';
    } else {
      properSize = sizeInBites / Math.pow(10, 9);
      units = 'GB';
    }

    return `${Math.round(properSize * 10) / 10} ${units}`;
  }
}
