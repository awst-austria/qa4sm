import {Component, OnInit} from '@angular/core';
import {MenubarModule} from 'primeng/menubar';
import {MenuItem} from 'primeng/api';
import {NGXLogger} from 'ngx-logger';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'qa4sm-ui';

  constructor(private logger:NGXLogger) {
  }

  ngOnInit(): void {
    this.logger.debug('Main app component init');
  }
}
