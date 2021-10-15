import {ComponentFixture, TestBed} from '@angular/core/testing';

import {AnomClimatologyComponent} from './anom-climatology.component';
import {BehaviorSubject} from 'rxjs';

describe('AnomClimatologyComponent', () => {
  let component: AnomClimatologyComponent;
  let fixture: ComponentFixture<AnomClimatologyComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AnomClimatologyComponent]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AnomClimatologyComponent);
    component = fixture.componentInstance;
    component.anomaliesModel = {
      method$: new BehaviorSubject('none'),
      description: '',
      anomaliesFrom$: new BehaviorSubject(new Date()),
      anomaliesTo$: new BehaviorSubject(new Date())
    };
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
