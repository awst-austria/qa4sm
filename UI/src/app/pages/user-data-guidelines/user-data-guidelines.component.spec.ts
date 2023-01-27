import {ComponentFixture, TestBed} from '@angular/core/testing';

import {UserDataGuidelinesComponent} from './user-data-guidelines.component';

describe('UserDataGuidelinesComponent', () => {
  let component: UserDataGuidelinesComponent;
  let fixture: ComponentFixture<UserDataGuidelinesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UserDataGuidelinesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UserDataGuidelinesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
