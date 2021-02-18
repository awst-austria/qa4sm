import {Injectable, TemplateRef} from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ToastService {
  toastDelay = 3500;

  constructor() {
  }

  toasts: any[] = [];

  show(textOrTpl: string | TemplateRef<any>, options: any = {}) {
    this.toasts.push({textOrTpl, ...options});
  }

  showSuccess(message: string) {
    this.show(message, {classname: 'bg-success text-light', delay: this.toastDelay});
  }

  showSuccessWithHeader(header: string,message: string) {
    this.show(message, {classname: 'bg-success text-light', delay: this.toastDelay, header: header});
  }

  showError(message: string) {
    this.show(message, {classname: 'bg-danger text-light', delay: this.toastDelay});
  }

  showErrorWithHeader(header: string,message: string) {
    this.show(message, {classname: 'bg-danger text-light', delay: this.toastDelay, header: header});
  }

  remove(toast: any) {
    this.toasts = this.toasts.filter(t => t !== toast);
  }
}
