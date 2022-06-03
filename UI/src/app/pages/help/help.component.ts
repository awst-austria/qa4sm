import {Component, OnInit} from '@angular/core';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {SettingsService} from '../../modules/core/services/global/settings.service';

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
  temporalSubsetting: string;
  tca: string;
  scaling: string;
  nameYourValidation: string;
  validateButton: string;
  myValidations: string;
  resultsOverview: string;
  resultsGraphs: string;
  publishingDialog: string;
  ismnNetworks: string;
  ismnDepths: string;
  datsetConfigurationComparison: string;
  validationSelectionsComparison: string;
  spatialExtentComparison: string;

  constructor(private globalParamsService: GlobalParamsService,
              public settingsService: SettingsService) {
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
    this.temporalSubsetting = plotsUrlPrefix + 'temporal_subsetting.png';
    this.tca = plotsUrlPrefix + 'metrics.png';
    this.scaling = plotsUrlPrefix + 'scaling.png';
    this.nameYourValidation = plotsUrlPrefix + 'name_your_validation.png';
    this.validateButton = plotsUrlPrefix + 'validate_button.png';
    this.myValidations = plotsUrlPrefix + 'my_validations.png';
    this.resultsOverview = plotsUrlPrefix + 'results_overview.png';
    this.resultsGraphs = plotsUrlPrefix + 'results_graphs.png';
    this.publishingDialog = plotsUrlPrefix + 'publishing_dialog.png';
    this.ismnNetworks = plotsUrlPrefix + 'networks.png';
    this.ismnDepths = plotsUrlPrefix + 'depths.png';
    this.datsetConfigurationComparison = plotsUrlPrefix + 'dataset-configuration-for-comparison.png';
    this.validationSelectionsComparison = plotsUrlPrefix + 'validation-selection-comparison.png';
    this.spatialExtentComparison = plotsUrlPrefix + 'spatial-extent-comparison.png';
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
