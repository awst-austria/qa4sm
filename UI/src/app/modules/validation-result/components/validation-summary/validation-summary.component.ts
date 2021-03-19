import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';

@Component({
  selector: 'qa-validation-summary',
  templateUrl: './validation-summary.component.html',
  styleUrls: ['./validation-summary.component.scss']
})
export class ValidationSummaryComponent implements OnInit {

  @Input() valrun: ValidationrunDto;
  constructor() { }

  ngOnInit(): void {
  }

}
