import {Injectable} from '@angular/core';
import {MessageService} from 'primeng/api';

@Injectable({
  providedIn: 'root'

})
export class ToastService {

  constructor(private messageService: MessageService) {
  }

  showSuccess(message: string) {
    this.messageService.add({key: 'global-toast', severity: 'success', detail: message});
  }

  showSuccessWithHeader(header: string, message: string) {
    this.messageService.add({key: 'global-toast', severity: 'success', summary: header, detail: message});
  }

  showError(message: string) {
    this.messageService.add({key: 'global-toast', severity: 'error', detail: message});
  }

  showErrorWithHeader(header: string, message: string) {
    this.messageService.add({key: 'global-toast', severity: 'error', summary: header, detail: message});
  }
}
