import {Component, OnInit} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {Observable} from 'rxjs';
import {HttpParams} from '@angular/common/http';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';

@Component({
  selector: 'qa-tracked-validations',
  templateUrl: './tracked-validations.component.html',
  styleUrls: ['./tracked-validations.component.scss']
})
export class TrackedValidationsComponent implements OnInit {

  constructor(private validationrunService: ValidationrunService) { }

  trackedRuns$: Observable<ValidationrunDto[]>;
  parameters = new HttpParams().set('tracked', String(true));

  ngOnInit(): void {
    this.trackedRuns$ = this.validationrunService.getCustomTrackedValidations();
  }

}
