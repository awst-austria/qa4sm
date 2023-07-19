import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ShareUserDataComponent} from './share-user-data.component';

describe('ShareUserDataComponent', () => {
  let component: ShareUserDataComponent;
  let fixture: ComponentFixture<ShareUserDataComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ShareUserDataComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ShareUserDataComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
