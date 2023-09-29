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

  deleteItems: MenuItem[];

  constructor(private validationrunService: ValidationrunService) {
  }

  ngOnInit() {
    this.deleteItems = [
      {
        label: 'Delete',
        icon: 'pi pi-fw pi-trash',
        items: [
          {
            label: 'Select all',
            icon: 'pi pi-fw pi-check-square',
            command: () => this.activateSelection(true)
          },
          {
            label: 'Select individually',
            icon: 'pi pi-fw pi-stop',
            command: () => this.activateSelection(false)
          }

        ]
      }
    ]
  }

  activateSelection(allSelected: boolean): void {
    this.selectionActive.emit({activate: true, selected: this.selectValidations(allSelected)})
    this.selectionActive$.next(true);
  }

  closeAndCleanSelection(): void {
    this.selectionActive.emit({activate: false, selected: this.selectValidations(false)})
    this.selectionActive$.next(false)

  }

  selectValidations(all: boolean): BehaviorSubject<string[]> {
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
    this.validationrunService.removeMultipleValidation(this.selectedValidationsId$.getValue()).subscribe(response =>{
      this.validationrunService.refreshComponent('page');
      this.closeAndCleanSelection()
    })
  }


}
