import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';
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
  public pageUrl = '/help';

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
  chosenFile: string;
  selectFile: string;
  uploadFileWindow: string;
  metadataWindow: string;
  uploadingSpinner: string;
  dataRow: string;
  userDataOnTheList: string;

  plotDivClass = 'w-12 align-items-center inline-block text-center'
  constructor(private globalParamsService: GlobalParamsService,
              public settingsService: SettingsService) {
  }

  @ViewChild('helpPage') container: ElementRef<HTMLElement>;

  ngOnInit(): void {
    this.helpPagePlots();
  }

  helpPagePlots(): void {
    this.menuMinus = plotsUrlPrefix + 'menu_minus.webp';
    this.menuPlus = plotsUrlPrefix + 'menu_plus.webp';
    this.datasetSelections = plotsUrlPrefix + 'data_set_selections.webp';
    this.intercomparison = plotsUrlPrefix + 'intercomparison.webp';
    this.referenceDatasetSelection = plotsUrlPrefix + 'reference_data_set_selections.webp';
    this.anomalies = plotsUrlPrefix + 'anomalies.webp';
    this.spatialSubsetting = plotsUrlPrefix + 'spatial_subsetting.webp';
    this.mapSelection = plotsUrlPrefix + 'map_selection.webp';
    this.temporalSubsetting = plotsUrlPrefix + 'temporal_subsetting.webp';
    this.tca = plotsUrlPrefix + 'metrics.webp';
    this.scaling = plotsUrlPrefix + 'scaling.webp';
    this.nameYourValidation = plotsUrlPrefix + 'name_your_validation.webp';
    this.validateButton = plotsUrlPrefix + 'validate_button.webp';
    this.myValidations = plotsUrlPrefix + 'my_validations.webp';
    this.resultsOverview = plotsUrlPrefix + 'results_overview.webp';
    this.resultsGraphs = plotsUrlPrefix + 'results_graphs.webp';
    this.publishingDialog = plotsUrlPrefix + 'publishing_dialog.webp';
    this.ismnNetworks = plotsUrlPrefix + 'networks.webp';
    this.ismnDepths = plotsUrlPrefix + 'depths.webp';
    this.datsetConfigurationComparison = plotsUrlPrefix + 'dataset-configuration-for-comparison.webp';
    this.validationSelectionsComparison = plotsUrlPrefix + 'validation-selection-comparison.webp';
    this.spatialExtentComparison = plotsUrlPrefix + 'spatial-extent-comparison.webp';
    this.metadataWindow = plotsUrlPrefix + 'metadata_window.webp';
    this.uploadFileWindow = plotsUrlPrefix + 'upload_file_window.webp';
    this.selectFile = plotsUrlPrefix + 'select_file.webp';
    this.chosenFile = plotsUrlPrefix + 'chosen_file.webp';
    this.uploadingSpinner = plotsUrlPrefix + 'uploading_spinner.webp';
    this.dataRow = plotsUrlPrefix + 'data_row.webp';
    this.userDataOnTheList = plotsUrlPrefix + 'user_data_on_the_list.webp';
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
