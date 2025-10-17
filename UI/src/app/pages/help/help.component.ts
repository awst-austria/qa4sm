import {Component} from '@angular/core';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';
import { RouterLink, RouterModule } from '@angular/router';
import { ScrollTop } from 'primeng/scrolltop';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faArchive, faFileDownload, faRedo, faStop } from '@fortawesome/free-solid-svg-icons';

const plotsUrlPrefix = '/static/images/help/';

@Component({
    selector: 'qa-help',
    imports: [RouterLink, RouterModule, FontAwesomeModule, ScrollTop],
    templateUrl: './help.component.html',
    styleUrls: ['./help.component.scss'],
    
})
export class HelpComponent {
  // Icons for bullet points
  faIcons = {
    faArchive,
    faStop,
    faFileDownload,
    faRedo
  };
  public pageUrl = '/help';

  menuMinus = plotsUrlPrefix + 'menu_minus.webp';
  menuPlus = plotsUrlPrefix + 'menu_plus.webp';
  datasetSelections = plotsUrlPrefix + 'data_set_selections.webp';
  intercomparison = plotsUrlPrefix + 'intercomparison.webp';
  referenceDatasetSelection = plotsUrlPrefix + 'reference_data_set_selections.webp';
  anomalies = plotsUrlPrefix + 'anomalies.webp';
  spatialSubsetting = plotsUrlPrefix + 'spatial_subsetting.webp';
  mapSelection = plotsUrlPrefix + 'map_selection.webp';
  temporalSubsetting = plotsUrlPrefix + 'temporal_subsetting.webp';
  tca = plotsUrlPrefix + 'metrics.webp';
  scaling = plotsUrlPrefix + 'scaling.webp';
  nameYourValidation = plotsUrlPrefix + 'name_your_validation.webp';
  validateButton = plotsUrlPrefix + 'validate_button.webp';
  myValidations = plotsUrlPrefix + 'my_validations.webp';
  resultsOverview = plotsUrlPrefix + 'results_overview.webp';
  resultsGraphs = plotsUrlPrefix + 'results_graphs.webp';
  publishingDialog = plotsUrlPrefix + 'publishing_dialog.webp';
  ismnNetworks = plotsUrlPrefix + 'networks.webp';
  ismnDepths = plotsUrlPrefix + 'depths.webp';
  datsetConfigurationComparison = plotsUrlPrefix + 'dataset-configuration-for-comparison.webp';
  validationSelectionsComparison = plotsUrlPrefix + 'validation-selection-comparison.webp';
  spatialExtentComparison = plotsUrlPrefix + 'spatial-extent-comparison.webp';
  metadataWindow = plotsUrlPrefix + 'metadata_window.webp';
  uploadFileWindow = plotsUrlPrefix + 'upload_file_window.webp';
  selectFile = plotsUrlPrefix + 'select_file.webp';
  chosenFile = plotsUrlPrefix + 'chosen_file.webp';
  uploadingSpinner = plotsUrlPrefix + 'uploading_spinner.webp';
  dataRow = plotsUrlPrefix + 'data_row.webp';
  userDataOnTheList = plotsUrlPrefix + 'user_data_on_the_list.webp';
  manageMultipleVals = plotsUrlPrefix + 'manage-multiple.webp';
  confirmMultipleVals = plotsUrlPrefix + 'confirm-multiple.webp';
  selectAction = plotsUrlPrefix + 'select-action.webp';
  selectedAction = plotsUrlPrefix + 'selected-action.webp';

  constructor(private globalParamsService: GlobalParamsService) {
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
