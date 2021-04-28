import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ResultFilesComponent} from './result-files.component';

describe('ResultFilesComponent', () => {
  let component: ResultFilesComponent;
  let fixture: ComponentFixture<ResultFilesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ResultFilesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ResultFilesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
