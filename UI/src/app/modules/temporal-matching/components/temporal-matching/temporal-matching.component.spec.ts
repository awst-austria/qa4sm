import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TemporalMatchingComponent } from './temporal-matching.component';

describe('TemporalMatchingComponent', () => {
  let component: TemporalMatchingComponent;
  let fixture: ComponentFixture<TemporalMatchingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TemporalMatchingComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TemporalMatchingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
