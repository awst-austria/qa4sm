import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyValidationsComponent } from './my-validations.component';

describe('MyValidationsComponent', () => {
  let component: MyValidationsComponent;
  let fixture: ComponentFixture<MyValidationsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyValidationsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MyValidationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
