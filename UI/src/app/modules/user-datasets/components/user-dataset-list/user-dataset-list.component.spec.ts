import {ComponentFixture, TestBed} from '@angular/core/testing';

import {UserDatasetListComponent} from './user-dataset-list.component';

describe('UserDatasetListComponent', () => {
  let component: UserDatasetListComponent;
  let fixture: ComponentFixture<UserDatasetListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UserDatasetListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UserDatasetListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
