import {Component, Input, OnInit} from '@angular/core';
import {ValidationPeriodModel} from './validation-period-model';

@Component({
  selector: 'qa-validation-period',
  templateUrl: './validation-period.component.html',
  styleUrls: ['./validation-period.component.scss']
})
export class ValidationPeriodComponent implements OnInit {

  @Input() validationPeriodModel:ValidationPeriodModel;

  constructor() { }

  ngOnInit(): void {
  }

}
