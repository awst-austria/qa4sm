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

  actions: ActionMenuItem[];
  selectOptions: MenuItem[];
  selectedAction: ActionMenuItem;

  constructor(private validationrunService: ValidationrunService,
              private toastService: ToastService) {
    this.actions = [
      {
        action: 'delete',
        label: 'Delete',
        icon: 'pi pi-fw pi-trash',
        command: () => this.deleteMultipleValidations()
      },
      {
        action: 'archive',
        label: 'Archive',
        icon: 'pi pi-fw pi-folder',
        command: () => this.archiveMultipleValidations(true)
      },
      {
        action: 'unarchive',
        label: 'Un-Archive',
        icon: 'pi pi-calendar',
        command: () => this.archiveMultipleValidations(false)
      }
    ];


    this.selectOptions = [{
      label: 'Select validations',
      items: [
        {
          label: 'All',
          icon: 'pi pi-fw pi-check-square',
          command: () => this.updateMultipleValidationAction(true),
        },
        {
          label: "Clear selection",
          icon: 'pi pi-fw pi-stop',
          command: () => this.updateMultipleValidationAction(false)
        }
      ]

    }];
  }

  selectValidationsIds(): string[] {
    return this.validations().filter(val => this.checkIfActionApplicable(val, this.selectedAction.action))
      .map(val => val.id);
  }

  checkIfActionApplicable(valrun: ValidationrunDto, action: string): boolean {
    return (action === 'unarchive') ? valrun.is_unpublished && valrun.is_archived : !valrun.is_archived
  }

  updateMultipleValidationAction(allSelected: boolean): void {
    this.multipleValidationAction.update(item => {
      item.active = true;
      item.allSelected = allSelected;
      item.action = this.selectedAction.action;
      item.selectedValidationIds = allSelected ? this.selectValidationsIds() : [];
      return item
    })
  }

  closeAndCleanSelection(): void {
    this.multipleValidationAction.update(item => {
      item = getDefaultValidationActionState();
      return item
    })
    this.selectedAction = null;
  }

  multipleValidationActionObserver = {
    next: () => {
      if (!confirm(`Do you really want to ${this.selectedAction.action} selected validations?`)) {
        return;
      }
      this.validationrunService.refreshComponent('page');
      this.closeAndCleanSelection();
    },
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

}
