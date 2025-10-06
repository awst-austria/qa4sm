import {ComponentFixture, TestBed} from '@angular/core/testing';

import {UserDataGuidelinesComponent2} from './user-data-guidelines2.component';

describe('UserDataGuidelinesComponent2', () => {
  let component: UserDataGuidelinesComponent2;
  let fixture: ComponentFixture<UserDataGuidelinesComponent2>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UserDataGuidelinesComponent2 ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UserDataGuidelinesComponent2);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
