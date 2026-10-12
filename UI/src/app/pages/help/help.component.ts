import { Component } from '@angular/core';

import { GlobalParamsService } from '../../modules/core/services/global/global-params.service';
import { RouterLink, RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  faArchive,
  faFileDownload,
  faStop,
} from '@fortawesome/free-solid-svg-icons';
import { PanelModule } from 'primeng/panel';
import { ImageModule } from 'primeng/image';

const plotsUrlPrefix = '/static/images/help/';

export type HelpSection =
  | 'home'
  | 'validate'
  | 'results'
  | 'my-validations'
  | 'published-validations'
  | 'upload'
  | 'upload-help'
  | 'my-datasets'
  | 'comparison'
  | 'api'
  | 'info'
  | 'comparison';

export interface NavItem {
  id: HelpSection | string;
  label: string;
  children?: NavItem[];
  expanded?: boolean;
  isGroup?: boolean;
}

@Component({
  selector: 'qa-help',
  imports: [
    RouterLink,
    RouterModule,
    FontAwesomeModule,
    PanelModule,
    ImageModule,
  ],
  templateUrl: './help.component.html',
  styleUrls: ['./help.component.scss'],
})
export class HelpComponent {
  faIcons = { faArchive, faStop, faFileDownload };

  activeSection: HelpSection = 'home';

  navItems: NavItem[] = [
    { id: 'home', label: 'Getting Started' },
    { id: 'validate', label: 'Validate' },
    {
      id: 'results',
      label: 'Results',
      expanded: false,
      isGroup: true,
      children: [
        { id: 'my-validations', label: 'My validations' },
        { id: 'published-validations', label: 'Published validations' },
      ],
    },
    {
      id: 'upload',
      label: 'Dataset upload',
      expanded: false,
      isGroup: true,
      children: [
        { id: 'my-datasets', label: 'My datasets' },
        { id: 'upload-help', label: 'Upload help' },
      ],
    },
    { id: 'comparison', label: 'Compare validations' },
    { id: 'api', label: 'Public API' },
    { id: 'info', label: 'Info' },
  ];

  /* images */
  myValidations = plotsUrlPrefix + 'my-validations.png';
  myResults1 = plotsUrlPrefix + 'my_validations_results.png';
  myResults2 = plotsUrlPrefix + 'my_validations_results2.png';
  myResults3 = plotsUrlPrefix + 'my_validations_results3.png';
  myuploads1 = plotsUrlPrefix + 'upload1.png';
  myuploads2 = plotsUrlPrefix + 'upload2.png';
  myuploads3 = plotsUrlPrefix + 'upload3.png';
  myuploads4 = plotsUrlPrefix + 'upload4.png';
  publishingDialog = plotsUrlPrefix + 'publishing_dialog.webp';
  datsetConfigurationComparison =
    plotsUrlPrefix + 'dataset-configuration-for-comparison.webp';
  validationSelectionsComparison =
    plotsUrlPrefix + 'validation-selection-comparison.webp';
  spatialExtentComparison = plotsUrlPrefix + 'spatial-extent-comparison.webp';
  metadataWindow = plotsUrlPrefix + 'metadata_window.webp';
  uploadFileWindow = plotsUrlPrefix + 'upload_file_window.webp';
  selectFile = plotsUrlPrefix + 'select_file.webp';
  chosenFile = plotsUrlPrefix + 'chosen_file.webp';
  uploadingSpinner = plotsUrlPrefix + 'uploading_spinner.webp';
  dataRow = plotsUrlPrefix + 'data_row.webp';
  userDataOnTheList = plotsUrlPrefix + 'user_data_on_the_list.webp';

  constructor(private globalParamsService: GlobalParamsService) {}

  setSection(id: HelpSection): void {
    this.activeSection = id;
  }

  isActive(id: HelpSection): boolean {
    return this.activeSection === id;
  }

  toggleGroup(item: NavItem): void {
    item.expanded = !item.expanded;
  }

  /** true if any child of the group is the active section */
  isGroupActive(item: NavItem): boolean {
    return !!item.children?.some((c) => this.activeSection === c.id);
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
