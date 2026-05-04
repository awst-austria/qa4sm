import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResultFilesSpatialComponent } from './result-files-spatial.component';

describe('ResultFilesSpatialComponent', () => {
  let component: ResultFilesSpatialComponent;
  let fixture: ComponentFixture<ResultFilesSpatialComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResultFilesSpatialComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ResultFilesSpatialComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
