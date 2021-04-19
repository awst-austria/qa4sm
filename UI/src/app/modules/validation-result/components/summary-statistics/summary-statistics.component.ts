import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';


@Component({
  selector: 'qa-summary-statistics',
  templateUrl: './summary-statistics.component.html',
  styleUrls: ['./summary-statistics.component.scss']
})
export class SummaryStatisticsComponent implements OnInit {
  @Input() validationRunId: any;
  @Input() referenceValidation: object;
  table$: Observable<string>;

  constructor(private validationService: ValidationrunService) {
  }

  ngOnInit(): void {
    console.log(this.validationRunId);
    this.getSummaryStatistics();
  }

  getSummaryStatistics(): void {
    const parameters = new HttpParams().set('id', this.validationRunId);
    this.table$ = this.validationService.getSummaryStatistics(parameters);
    // this.validationService.getSummaryStatistics(parameters).subscribe(data => {
    //   this.table = data;
    // });
  }
  // getSummaryStatistics(): void {
  //   const summaryStatisticsUrl = `/api/summary-statistics?id=${this.validationRunId}`;
  //   const params = new HttpParams().set('id', this.validationRunId);
  //   this.httpClient.get(summaryStatisticsUrl).subscribe(data => console.log(data));
  //   // this.httpClient.get(summaryStatisticsUrl, {params}).map(r => r.text()).subscribe(v => this.table = v);
  // }

}
