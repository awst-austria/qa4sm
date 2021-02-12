import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';

@Component({
  selector: 'app-validation',
  templateUrl: './validation.component.html',
  styleUrls: ['./validation.component.scss']
})
export class ValidationComponent implements OnInit {
  validationId: String = '';

  constructor(private route: ActivatedRoute) {
    this.route.params.subscribe(params => {
      this.validationId = params['validationId'];
    });
  }

  ngOnInit(): void {
  }

}
