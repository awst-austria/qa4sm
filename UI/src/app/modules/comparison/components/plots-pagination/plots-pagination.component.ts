import {Component, Input, OnInit} from '@angular/core';
import {ComparisonService} from "../../services/comparison.service";
import {ValidationrunDto} from "../../../core/services/validation-run/validationrun.dto";
import {HttpParams} from "@angular/common/http";
import {ComparisonDto} from "../../services/comparison.dto";
import {PlotConfigurationDto} from "../../services/plot-configuration.dto";
import {Observable} from "rxjs";

@Component({
  selector: 'qa-plots-pagination',
  templateUrl: './plots-pagination.component.html',
  styleUrls: ['./plots-pagination.component.scss'],
})
export class PlotsPaginationComponent implements OnInit {
  @Input() comparisonObj: ComparisonDto;
  @Input() comparisonPlot: PlotConfigurationDto;
  comparisonTable$: Observable<string>;


  constructor(private comparisonService: ComparisonService,) {
  }

  ngOnInit(): void {
    this.getComparisonObject();
    this.getComparisonPlot();
  }

  getComparisonObject(): void {
    //const parameters = new HttpParams().set('ids', this.comparisonObj.ids);
  }

  getComparisonPlot(): void {
    const parameters = new HttpParams().set('metric', this.comparisonPlot.metric);
  }

  getDifferenceTable(): void{
    //this.comparisonTable$ = this.comparisonService.getComparisonTable()
  }

  getComparisonTableAsCsv(): void{
    this.comparisonService.downloadComparisonTableCsv();
  }

}
