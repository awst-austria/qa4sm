import {ComponentFixture, TestBed} from '@angular/core/testing';

import {UserFileUploadComponent} from './user-file-upload.component';

describe('UserFileUploadComponent', () => {
  let component: UserFileUploadComponent;
  let fixture: ComponentFixture<UserFileUploadComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UserFileUploadComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UserFileUploadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
