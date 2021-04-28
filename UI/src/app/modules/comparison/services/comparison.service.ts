import { Injectable } from '@angular/core';
import {environment} from "../../../../environments/environment";
import {HttpClient} from "@angular/common/http";

const urlPrefix = environment.API_URL + 'api';
const resultsComparisonUrl: string = urlPrefix + '/results-comparison';
const comparisonPlotUrl: string = urlPrefix + '/comparison-plot';
const comparisonTable: string = urlPrefix + '/comparison-table';
const downloadComparisonTableUrl: string = urlPrefix + '/download-comparison-table'

@Injectable({
  providedIn: 'root'
})
export class ComparisonService {

  constructor(private httpClient: HttpClient) {
  }

  getComparisonObject(){
    return this.httpClient.get(resultsComparisonUrl);
  }
  // to complete
  getComparisonTable(){
    return this.httpClient.get(comparisonTable);
  }

  getComparisonPlot(){
    return this.httpClient.get(comparisonPlotUrl);
  }

  downloadComparisonTableCsv(){
    return this.httpClient.get(downloadComparisonTableUrl)
  }

}
