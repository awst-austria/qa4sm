import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PinnedValidationsComponent } from './pinned-validations.component';

describe('PinnedValidationsComponent', () => {
  let component: PinnedValidationsComponent;
  let fixture: ComponentFixture<PinnedValidationsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PinnedValidationsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PinnedValidationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
