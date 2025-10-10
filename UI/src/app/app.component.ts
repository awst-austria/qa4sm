import {Component, OnInit, ViewChild} from '@angular/core';
import {NGXLogger} from 'ngx-logger';


@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss'],
    standalone: false
})
export class AppComponent implements OnInit {
  title = 'qa4sm-ui';

  constructor(private logger: NGXLogger) {
  }

  ngOnInit(): void {
    this.logger.debug('Main app component init');
  }

}
