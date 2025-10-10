import {Component, input} from '@angular/core';

@Component({
    selector: 'qa-maintenance-mode',
    imports: [],
    templateUrl: './maintenance-mode.component.html',
    styleUrl: './maintenance-mode.component.scss'
})
export class MaintenanceModeComponent {
  action = input('');
}
