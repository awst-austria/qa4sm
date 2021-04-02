import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ScalingComponent} from './scaling.component';

describe('ScalingComponent', () => {
  let component: ScalingComponent;
  let fixture: ComponentFixture<ScalingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ScalingComponent]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ScalingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
