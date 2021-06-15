import {Component, OnInit} from '@angular/core';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {WebsiteGraphicsService} from '../../modules/core/services/global/website-graphics.service';
import {Observable} from 'rxjs';
import {HttpParams} from '@angular/common/http';
import {PlotDto} from '../../modules/core/services/global/plot.dto';
import {SafeUrl} from '@angular/platform-browser';

const plotsUrlPrefix = '/static/images/help/';
@Component({
  selector: 'qa-help',
  templateUrl: './help.component.html',
  styleUrls: ['./help.component.scss']
})
export class HelpComponent implements OnInit {
  // Icons for bullet points
  faIcons = {faArchive: fas.faArchive,
    faStop: fas.faStop,
    faFileDownload: fas.faFileDownload,
    faRedo: fas.faRedo};


  menuMinus$: Observable<PlotDto>;
  menuPlus$: Observable<PlotDto>;
  datasetSelections$: Observable<PlotDto>;
  intercomparison$: Observable<PlotDto>;
  referenceDatasetSelection$: Observable<PlotDto>;
  anomalies$: Observable<PlotDto>;
  spatialSubsetting$: Observable<PlotDto>;
  mapSelection$: Observable<PlotDto>;
  validationPeriod$: Observable<PlotDto>;
  tca$: Observable<PlotDto>;
  scaling$: Observable<PlotDto>;
  nameYourValidation$: Observable<PlotDto>;
  validateButton$: Observable<PlotDto>;
  myValidations$: Observable<PlotDto>;
  resultsOverview$: Observable<PlotDto>;
  resultsGraphs$: Observable<PlotDto>;
  publicationDialog$: Observable<PlotDto>;

  constructor(private globalParamsService: GlobalParamsService,
              private plotService: WebsiteGraphicsService) { }

  ngOnInit(): void {
    this.getHelpPagePlots();
  }
  getHelpPagePlots(): void{
    this.menuMinus$ = this.getPlot(plotsUrlPrefix + 'menu_minus.png');
    this.menuPlus$ = this.getPlot(plotsUrlPrefix + 'menu_plus.png');
    this.datasetSelections$ = this.getPlot(plotsUrlPrefix + 'data_set_selections.png');
    this.intercomparison$ = this.getPlot(plotsUrlPrefix + 'intercomparison.png');
    this.referenceDatasetSelection$ = this.getPlot(plotsUrlPrefix + 'reference_data_set_selections.png');
    this.anomalies$ = this.getPlot(plotsUrlPrefix + 'anomalies.png');
    this.spatialSubsetting$ = this.getPlot(plotsUrlPrefix + 'spatial_subsetting.png');
    this.mapSelection$ = this.getPlot(plotsUrlPrefix + 'map_selection.png');
    this.validationPeriod$ = this.getPlot(plotsUrlPrefix + 'validation_period.png');
    this.tca$ = this.getPlot(plotsUrlPrefix + 'tca.png');
    this.scaling$ = this.getPlot(plotsUrlPrefix + 'scaling.png');
    this.nameYourValidation$ = this.getPlot(plotsUrlPrefix + 'name_your_validation.png');
    this.validateButton$ = this.getPlot(plotsUrlPrefix + 'validate_button.png');
    this.myValidations$ = this.getPlot(plotsUrlPrefix + 'my_validations.png');
    this.resultsOverview$ = this.getPlot(plotsUrlPrefix + 'results_overview.png');
    this.resultsGraphs$ = this.getPlot(plotsUrlPrefix + 'results_graphs.png');
    this.publicationDialog$ = this.getPlot(plotsUrlPrefix + 'publication_dialog.png');
  }

  getPlot(plot): Observable<any>{
    const params = new HttpParams().set('file', plot);
    return this.plotService.getSinglePlot(params);
  }

  getAdminMail(): string {
    return this.globalParamsService.globalContext.admin_mail;
   }
  getExpiryPeriod(): string {
    return this.globalParamsService.globalContext.expiry_period;
   }
  getWarningPeriod(): string {
    return this.globalParamsService.globalContext.warning_period;
   }

  sanitizePlotUrl(plotUrl: string): SafeUrl{
    return this.plotService.sanitizePlotUrl(plotUrl);
  }

}
