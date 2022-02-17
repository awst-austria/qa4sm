import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ExtentVisualizationComponent} from './extent-visualization.component';

describe('ExtentVisualizationComponent', () => {
  let component: ExtentVisualizationComponent;
  let fixture: ComponentFixture<ExtentVisualizationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExtentVisualizationComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExtentVisualizationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
