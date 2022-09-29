import {ComponentFixture, TestBed} from '@angular/core/testing';

import {UserDataRowComponent} from './user-data-row.component';

describe('UserDataRowComponent', () => {
  let component: UserDataRowComponent;
  let fixture: ComponentFixture<UserDataRowComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UserDataRowComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UserDataRowComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
