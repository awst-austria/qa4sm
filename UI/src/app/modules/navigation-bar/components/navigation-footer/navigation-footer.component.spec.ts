import {ComponentFixture, TestBed} from '@angular/core/testing';

import {NavigationFooterComponent} from './navigation-footer.component';

describe('NavigationFooterComponent', () => {
  let component: NavigationFooterComponent;
  let fixture: ComponentFixture<NavigationFooterComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [NavigationFooterComponent]
    });
    fixture = TestBed.createComponent(NavigationFooterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
