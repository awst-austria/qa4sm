import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PublishedValidationsComponent } from './published-validations.component';

describe('PublishedValidationsComponent', () => {
  let component: PublishedValidationsComponent;
  let fixture: ComponentFixture<PublishedValidationsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PublishedValidationsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PublishedValidationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
