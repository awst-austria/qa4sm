import {Component, Input, OnInit} from '@angular/core';
import {ExtentModel} from "./extent-model";


@Component({
  selector: 'qa-spatial-extent',
  templateUrl: './spatial-extent.component.html',
  styleUrls: ['./spatial-extent.component.scss']
})
export class SpatialExtentComponent implements OnInit {

  @Input() extentModel: ExtentModel;
  @Input() disabled: boolean = false;

  constructor() {

  }

  ngOnInit(): void {
  }

}
