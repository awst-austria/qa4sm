import {Component, OnInit} from '@angular/core';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';
import {fas} from '@fortawesome/free-solid-svg-icons';

const plotsUrlPrefix = '/static/images/help/';

@Component({
  selector: 'qa-help',
  templateUrl: './help.component.html',
  styleUrls: ['./help.component.scss']
})
export class HelpComponent implements OnInit {
  // Icons for bullet points
  faIcons = {
    faArchive: fas.faArchive,
    faStop: fas.faStop,
    faFileDownload: fas.faFileDownload,
    faRedo: fas.faRedo
  };

  menuMinus: string;
  menuPlus: string;
  datasetSelections: string;
  intercomparison: string;
  referenceDatasetSelection: string;
  anomalies: string;
  spatialSubsetting: string;
  mapSelection: string;
  validationPeriod: string;
  tca: string;
  scaling: string;
  nameYourValidation: string;
  validateButton: string;
  myValidations: string;
  resultsOverview: string;
  resultsGraphs: string;
  publicationDialog: string;

  constructor(private globalParamsService: GlobalParamsService) {
  }

  ngOnInit(): void {
    this.helpPagePlots();
  }

  helpPagePlots(): void {
    this.menuMinus = plotsUrlPrefix + 'menu_minus.png';
    this.menuPlus = plotsUrlPrefix + 'menu_plus.png';
    this.datasetSelections = plotsUrlPrefix + 'data_set_selections.png';
    this.intercomparison = plotsUrlPrefix + 'intercomparison.png';
    this.referenceDatasetSelection = plotsUrlPrefix + 'reference_data_set_selections.png';
    this.anomalies = plotsUrlPrefix + 'anomalies.png';
    this.spatialSubsetting = plotsUrlPrefix + 'spatial_subsetting.png';
    this.mapSelection = plotsUrlPrefix + 'map_selection.png';
    this.validationPeriod = plotsUrlPrefix + 'validation_period.png';
    this.tca = plotsUrlPrefix + 'tca.png';
    this.scaling = plotsUrlPrefix + 'scaling.png';
    this.nameYourValidation = plotsUrlPrefix + 'name_your_validation.png';
    this.validateButton = plotsUrlPrefix + 'validate_button.png';
    this.myValidations = plotsUrlPrefix + 'my_validations.png';
    this.resultsOverview = plotsUrlPrefix + 'results_overview.png';
    this.resultsGraphs = plotsUrlPrefix + 'results_graphs.png';
    this.publicationDialog = plotsUrlPrefix + 'publication_dialog.png';
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

}
