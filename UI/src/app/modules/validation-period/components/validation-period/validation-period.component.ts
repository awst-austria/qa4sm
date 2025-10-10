import {Component, Input} from '@angular/core';
import {ValidationPeriodModel} from './validation-period-model';

@Component({
    selector: 'qa-validation-period',
    templateUrl: './validation-period.component.html',
    styleUrls: ['./validation-period.component.scss'],
    standalone: false
})
export class ValidationPeriodComponent {

  @Input() validationPeriodModel: ValidationPeriodModel;

  constructor() { }
}
