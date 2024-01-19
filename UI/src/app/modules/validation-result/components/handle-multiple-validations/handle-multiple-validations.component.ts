import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {MenuItem} from 'primeng/api';

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

  selectOptions: MenuItem[];

  action: string = null;
  buttonLabel: string;
  allSelected: boolean;
  actions: any[];
  numberOfAllValidations: number;

  constructor(private validationrunService: ValidationrunService) {
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
      this.validations.forEach(val => {
        if (this.checkIfActionApplicable(val, action)) {
          selectedValidations.push(val.id)
        }
      })
    }
    this.numberOfAllValidations = selectedValidations.length;
    return new BehaviorSubject(selectedValidations)
  }

  checkIfActionApplicable(valrun: ValidationrunDto, action: string): boolean{
    let condition = valrun.is_unpublished

    if (action === 'unarchive'){
      condition = condition && valrun.is_archived
    } else if (action === 'archive'){
      condition = condition && !valrun.is_archived
    }
    return condition;
  }


  emitSelection(select: boolean): void {
    this.selectionActive.emit({
      active: true,
      selected: this.selectValidations(select, this.action),
      allSelected: select,
      action: this.action
    })
  }

  actionChange(): void{
    if (!this.selectionActive$.value){
      this.selectionActive$.next(true);
    }
    this.selectionActive.emit({
      active: true,
      selected: new BehaviorSubject([]),
      allSelected: false,
      action: this.action
    })

    this.buttonLabel = this.actions.find(element => element.action == this.action).label
  }

  closeAndCleanSelection(): void {
    this.selectionActive.emit({activate: false, selected: this.selectValidations(false, null)})
    this.selectionActive$.next(false)
    this.action = null;
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
