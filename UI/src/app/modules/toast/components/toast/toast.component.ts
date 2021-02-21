import {Component, OnInit, TemplateRef} from '@angular/core';
import {ToastService} from '../../services/toast.service';

@Component({
  selector: 'qa-toast',
  template: `
    <ngb-toast
      *ngFor="let toast of toastService.toasts"
      [class]="toast.classname"
      [autohide]="true"
      [header]="toast.header || ''"
      [delay]="toast.delay || 5000"
      (hidden)="toastService.remove(toast)">
      <ng-template [ngIf]="isTemplate(toast)" [ngIfElse]="text">
        <ng-template [ngTemplateOutlet]="toast.textOrTpl"></ng-template>
      </ng-template>

      <ng-template #text>{{ toast.textOrTpl }}</ng-template>
    </ngb-toast>
  `,
  host: {'[class.ngb-toasts]': 'true'},
  styleUrls: ['./toast.component.scss']
})
export class ToastComponent implements OnInit {

  constructor(public toastService: ToastService) {
  }

  isTemplate(toast: any) {
    return toast.textOrTpl instanceof TemplateRef;
  }

  ngOnInit(): void {
  }

}
