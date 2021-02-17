import {Component, OnInit} from '@angular/core';
import {NGXLogger} from 'ngx-logger';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  title = 'qa4sm-ui';
  isCollapsed = true;

  constructor(private logger: NGXLogger) {
  }

  ngOnInit(): void {
    this.logger.debug('Main app component init');
  }
}
