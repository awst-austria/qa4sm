import {ComponentFixture, TestBed} from '@angular/core/testing';

import {HandleMultipleValidationsComponent} from './handle-multiple-validations.component';

describe('HandleMultipleValidationsComponent', () => {
  let component: HandleMultipleValidationsComponent;
  let fixture: ComponentFixture<HandleMultipleValidationsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HandleMultipleValidationsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HandleMultipleValidationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
