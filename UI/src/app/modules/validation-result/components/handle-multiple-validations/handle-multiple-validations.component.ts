import {Component, input, model, OnInit} from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {MenuItem} from 'primeng/api';
import {CustomHttpError} from '../../../core/services/global/http-error.service';
import {ToastService} from '../../../core/services/toast/toast.service';

@Component({
  selector: 'qa-handle-multiple-validations',
  templateUrl: './handle-multiple-validations.component.html',
  styleUrls: ['./handle-multiple-validations.component.scss']
})
export class HandleMultipleValidationsComponent implements OnInit {
  validations = input([] as ValidationrunDto[]);
  multipleValidationAction = model({} as {
    active: boolean,
    action: string,
    allSelected: boolean,
    selectedValidationIds: string[]
  });

  selectionActive$ = new BehaviorSubject(false);

  deleteItems: {};
  archiveItems: {};
  unArchiveItems: {};

  selectOptions: MenuItem[];

  action: string = null;
  buttonLabel: string;
  allSelected: boolean;
  actions: any[];
  numberOfAllValidations: number;

  constructor(private validationrunService: ValidationrunService,
              private toastService: ToastService) {
  }

  ngOnInit() {

    this.deleteItems =
      {
        action: 'delete',
        label: 'Delete',
        icon: 'pi pi-fw pi-trash',
      };

    this.archiveItems =
      {
        action: 'archive',
        label: 'Archive',
        icon: 'pi pi-fw pi-folder',
      };

    this.unArchiveItems =
      {
        action: 'unarchive',
        label: 'Un-Archive',
        icon: 'pi pi-calendar',
      };

    this.actions = [
      this.deleteItems,
      this.archiveItems,
      this.unArchiveItems
    ];

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


  selectValidations(select: boolean, action: string): BehaviorSubject<string[]> {
    const selectedValidations = [];
    const select_archived = action === 'unarchive';
    if (select) {
      this.validations().forEach(val => {
        if (this.checkIfActionApplicable(val, action)) {
          selectedValidations.push(val.id)
        }
      })
    }
    console.log('event', selectedValidations);
    this.numberOfAllValidations = selectedValidations.length;
    return new BehaviorSubject(selectedValidations)
  }

  selectValidationsIds(select: boolean, action: string): string[] {
    const selectedValidations = [];
    const select_archived = action === 'unarchive';
    if (select) {
      this.validations().forEach(val => {
        if (this.checkIfActionApplicable(val, action)) {
          selectedValidations.push(val.id)
        }
      })
    }
    this.numberOfAllValidations = selectedValidations.length;
    console.log('form', selectedValidations);
    return selectedValidations;
  }

  checkIfActionApplicable(valrun: ValidationrunDto, action: string): boolean {
    let condition = valrun.is_unpublished

    if (action === 'unarchive') {
      condition = condition && valrun.is_archived
    } else if (action === 'archive') {
      condition = condition && !valrun.is_archived
    }
    return condition;
  }


  emitSelection(select: boolean): void {
    this.multipleValidationAction.update(item => {
      item.active = true;
      item.allSelected = select;
      item.action = this.action;
      item.selectedValidationIds = this.selectValidationsIds(select, this.action);
      return item
    })
  }

  actionChange(): void {
    if (!this.selectionActive$.value) {
      this.selectionActive$.next(true);
    }


    this.multipleValidationAction.update(item => {
      item.active = true;
      item.allSelected = false;
      item.action = this.action;
      item.selectedValidationIds = [];
      return item
    })

    this.buttonLabel = this.actions.find(element => element.action == this.action).label
  }

  closeAndCleanSelection(): void {
    this.multipleValidationAction.update(item => {
      item.active = false;
      item.allSelected = false;
      item.action = null;
      item.selectedValidationIds = this.selectValidationsIds(false, null);
      return item
    })


    this.selectionActive$.next(false)
    this.action = null;
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
    if (!confirm(`Do you really want to ${this.action} selected validations?`)) {
      return;
    }
    if (this.action === 'delete') {
      this.deleteMultipleValidations()
    } else if (this.action === 'archive' || this.action === 'unarchive') {
      this.archiveMultipleValidations(this.action === 'archive')
    }
    this.closeAndCleanSelection()
  }


}
