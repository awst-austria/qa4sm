import {Component, input, model} from '@angular/core';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {MenuItem} from 'primeng/api';
import {CustomHttpError} from '../../../core/services/global/http-error.service';
import {ToastService} from '../../../core/services/toast/toast.service';
import {ActionMenuItem, getDefaultValidationActionState, MultipleValidationAction} from "./multiple-validation-action";

@Component({
  selector: 'qa-handle-multiple-validations',
  templateUrl: './handle-multiple-validations.component.html',
  styleUrls: ['./handle-multiple-validations.component.scss']
})
export class HandleMultipleValidationsComponent {
  validations = input([] as ValidationrunDto[]);
  multipleValidationAction = model({} as MultipleValidationAction);


  deleteItems: ActionMenuItem =
    {
      action: 'delete',
      label: 'Delete',
      icon: 'pi pi-fw pi-trash',
    };

  archiveItems: ActionMenuItem =
    {
      action: 'archive',
      label: 'Archive',
      icon: 'pi pi-fw pi-folder',
    };
  unArchiveItems: ActionMenuItem =
    {
      action: 'unarchive',
      label: 'Un-Archive',
      icon: 'pi pi-calendar',
    };

  actions = [
    this.deleteItems,
    this.archiveItems,
    this.unArchiveItems
  ];

  selectOptions: MenuItem[];

  action: string = null;

  selectedAction: ActionMenuItem;
  constructor(private validationrunService: ValidationrunService,
              private toastService: ToastService) {
    this.selectOptions = [{
      label: 'Select validations',
      items: [
        {
          label: 'All',
          icon: 'pi pi-fw pi-check-square',
          command: () => this.emitSelection(true),
        },
        {
          label: "Clear selection",
          icon: 'pi pi-fw pi-stop',
          command: () => this.emitSelection(false)
        }
      ]

    }];
  }

  selectValidationsIds(): string[] {
    const selectedValidations = [];
    this.validations().forEach(val => {
      if (this.checkIfActionApplicable(val, this.selectedAction.action)) {
        selectedValidations.push(val.id)
      }
    })
    return selectedValidations;
  }

  checkIfActionApplicable(valrun: ValidationrunDto, action: string): boolean {
    return (action === 'unarchive') ? valrun.is_unpublished && valrun.is_archived : !valrun.is_archived
  }


  emitSelection(select: boolean): void {
    this.multipleValidationAction.update(item => {
      item.allSelected = select;
      item.action = this.selectedAction.action;
      item.selectedValidationIds = this.selectValidationsIds();
      return item
    })
  }

  actionChange(): void {
    this.multipleValidationAction.update(item => {
      item.active = true;
      item.allSelected = false;
      item.action = this.selectedAction.action;
      item.selectedValidationIds = [];
      return item
    })
  }

  closeAndCleanSelection(): void {
    this.multipleValidationAction.update(item => {
      item = getDefaultValidationActionState();
      return item
    })

    this.selectedAction.action = null;
  }

  multipleValidationActionObserver = {
    next: () => this.validationrunService.refreshComponent('page'),
    error: (error: CustomHttpError) =>
      this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message)
  }


  deleteMultipleValidations(): void {
    this.validationrunService.removeMultipleValidation(this.multipleValidationAction().selectedValidationIds)
      .subscribe(this.multipleValidationActionObserver)
  }

  archiveMultipleValidations(archive: boolean): void {
    this.validationrunService.archiveMultipleValidation(this.multipleValidationAction().selectedValidationIds, archive)
      .subscribe(this.multipleValidationActionObserver)
  }

  handleMultipleValidations(): void {
    if (!confirm(`Do you really want to ${this.selectedAction.action} selected validations?`)) {
      return;
    }
    if (this.selectedAction.action === 'delete') {
      this.deleteMultipleValidations()
    } else if (this.selectedAction.action === 'archive' || this.selectedAction.action === 'unarchive') {
      this.archiveMultipleValidations(this.selectedAction.action === 'archive')
    }
    this.closeAndCleanSelection()
  }


}
