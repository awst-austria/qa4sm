import {Component, Input, Output, OnInit, EventEmitter} from '@angular/core';
import {ExtentModel} from "./extent-model";


@Component({
  selector: 'qa-spatial-extent',
  templateUrl: './spatial-extent.component.html',
  styleUrls: ['./spatial-extent.component.scss']
})
export class SpatialExtentComponent implements OnInit {

  @Input() extentModel: ExtentModel;
  @Input() disabled: boolean;

  @Output() onChecked: EventEmitter<any> = new EventEmitter<any>();

  constructor() {
  }

  ngOnInit(): void {
  }

  spatialExtentChange(event: any) {
    // assign the new extent selection to the comparison settings
    this.onChecked.emit(!event.checked)
  }
}
