import {Component, EventEmitter, Input, Output} from '@angular/core';
import {ExtentModel} from './extent-model';


@Component({
    selector: 'qa-spatial-extent',
    templateUrl: './spatial-extent.component.html',
    styleUrls: ['./spatial-extent.component.scss'],
    standalone: false
})
export class SpatialExtentComponent {

  @Input() extentModel: ExtentModel;
  @Input() disabled: boolean;
  @Output() ifChecked: EventEmitter<any> = new EventEmitter<any>();

  constructor() {
  }

  spatialExtentChange(event: any): void{
    // assign the new extent selection to the comparison settings
    this.ifChecked.emit(!event);
  }
}
