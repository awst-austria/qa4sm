import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {MenuItem} from 'primeng/api';
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

  deleteItems: MenuItem;
  archiveItems: MenuItem;
  items: MenuItem[];

  action: string = null;
  actions: {}

  constructor(private validationrunService: ValidationrunService) {
  }

  ngOnInit() {
    this.deleteItems =
      {
        label: 'Delete',
        icon: 'pi pi-fw pi-trash',
        items: [
          {
            label: 'Select all',
            icon: 'pi pi-fw pi-check-square',
            command: () => this.activateSelection(true, 'delete')
          },
          {
            label: 'Select individually',
            icon: 'pi pi-fw pi-stop',
            command: () => this.activateSelection(false, 'delete')
          }
        ]
      }

    this.archiveItems =
      {
        label: 'Archive',
        icon: 'pi pi-fw pi-folder',
        items: [
          {
            label: 'Select all',
            icon: 'pi pi-fw pi-check-square',
            command: () => this.activateSelection(true, 'archive')
          },
          {
            label: 'Select individually',
            icon: 'pi pi-fw pi-stop',
            command: () => this.activateSelection(false, 'archive')
          }

        ]
      }

    this.items = [
      {
        label: 'Modify multiple validations',
        items: [
          this.deleteItems,
          this.archiveItems
        ]

      }
    ]
    this.actions = {
      delete: this.deleteItems,
      archive: this.archiveItems
    }
  }

  activateSelection(allSelected: boolean, action: string): void {
    this.selectionActive.emit({activate: true, selected: this.selectValidations(allSelected, action)})
    this.selectionActive$.next(true);
    this.action = action;
  }

  closeAndCleanSelection(): void {
    this.selectionActive.emit({activate: false, selected: this.selectValidations(false, null)})
    this.selectionActive$.next(false)
    this.action = null;
  }

  selectValidations(all: boolean, action: string): BehaviorSubject<string[]> {
    const selectedValidations = [];
    if (all) {
      this.validations.forEach(val => {
        if (!val.is_archived && val.is_unpublished) {
          selectedValidations.push(val.id)
        }
      })
    }
    return new BehaviorSubject(selectedValidations)
  }


  deleteMultipleValidations(): void {
    if (!confirm('Do you really want to delete selected validations?')) {
      return;
    }
    this.validationrunService.removeMultipleValidation(this.selectedValidationsId$.getValue()).subscribe(response => {
      this.validationrunService.refreshComponent('page');
    })
  }

  archiveMultipleValidations(): void {
    if (!confirm('Do you really want to delete selected validations?')) {
      return;
    }
    this.validationrunService.archiveMultipleValidation(this.selectedValidationsId$.getValue()).subscribe(response => {
      this.validationrunService.refreshComponent('page');
    })
  }

  handleMultipleValidations(): void {
    if (this.action === 'delete') {
      this.deleteMultipleValidations()
    } else if (this.action === 'archive') {
      this.archiveMultipleValidations()
    }
    this.closeAndCleanSelection()
  }


}
