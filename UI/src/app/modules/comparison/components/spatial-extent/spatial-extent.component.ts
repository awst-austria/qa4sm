import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {ExtentModel} from './extent-model';


@Component({
  selector: 'qa-spatial-extent',
  templateUrl: './spatial-extent.component.html',
  styleUrls: ['./spatial-extent.component.scss']
})
export class SpatialExtentComponent implements OnInit {
  spatialExtentChecked = false;

  @Input() extentModel: ExtentModel;
  @Input() disabled: boolean;
  @Output() ifChecked: EventEmitter<any> = new EventEmitter<any>();

  constructor() {
  }

  ngOnInit(): void {
  }

  spatialExtentChange(event: any): void{
    // assign the new extent selection to the comparison settings
    this.ifChecked.emit(!event);
  }
}
