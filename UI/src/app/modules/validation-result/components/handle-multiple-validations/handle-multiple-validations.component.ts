import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';

@Component({
  selector: 'qa-handle-multiple-validations',
  templateUrl: './handle-multiple-validations.component.html',
  styleUrls: ['./handle-multiple-validations.component.scss']
})
export class HandleMultipleValidationsComponent implements OnInit {
  @Output() selectionActive = new EventEmitter();
  @Input() validations: ValidationrunDto[];
  @Input() selectedValidationsId$: BehaviorSubject<string[]>;
  @Output() doUpdate = new EventEmitter();

  selectionActive$ = new BehaviorSubject(false);

  deleteItems: {};
  archiveItems: {};
  unArchiveItems: {};

  selectOptions: any[];

  action: string = null;
  allSelected: boolean;
  actions: any[];

  constructor(private validationrunService: ValidationrunService) {
  }

  ngOnInit() {
    this.deleteItems =
      {
        action: 'delete',
        label: 'Delete',
        icon: 'pi pi-fw pi-trash',
      }

    this.archiveItems =
      {
        action: 'archive',
        label: 'Archive',
        icon: 'pi pi-fw pi-folder',
      }

    this.unArchiveItems =
      {
        action: 'unarchive',
        label: 'Un-Archive',
        icon: 'pi pi-calendar',
      }

    this.actions = [
      this.deleteItems,
      this.archiveItems,
      this.unArchiveItems
    ]

    this.selectOptions = [
      {label: 'Select all', allSelected: true},
      {label: 'Select individually', allSelected: false},
    ]
  }

  startSelection(selectAll = false): void {
    this.selectionActive$.next(true);
    this.selectionActive.emit({
      activate: true,
      selected: this.selectValidations(selectAll, this.action),
      action: this.action
    })
  }

  closeAndCleanSelection(): void {
    this.selectionActive.emit({activate: false, selected: this.selectValidations(false, null)})
    this.selectionActive$.next(false)
    this.action = null;
    this.allSelected = false;
  }


  selectValidations(all: boolean, action: string): BehaviorSubject<string[]> {
    const selectedValidations = [];
    const select_archived = action === 'unarchive';
    if (all && action !== 'unarchived') {
      this.validations.forEach(val => {
        if (val.is_archived === select_archived && val.is_unpublished) {
          selectedValidations.push(val.id)
        }
      })
    }
    return new BehaviorSubject(selectedValidations)
  }


  deleteMultipleValidations(): void {
    this.validationrunService.removeMultipleValidation(this.selectedValidationsId$.getValue()).subscribe(response => {
      this.validationrunService.refreshComponent('page');
    })
  }

  archiveMultipleValidations(archive: boolean): void {
    this.validationrunService.archiveMultipleValidation(this.selectedValidationsId$.getValue(), archive).subscribe(response => {
      this.validationrunService.refreshComponent('page');
    })
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
