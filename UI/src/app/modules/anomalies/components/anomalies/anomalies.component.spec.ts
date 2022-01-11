import {ComponentFixture, TestBed} from '@angular/core/testing';

import {AnomaliesComponent} from './anomalies.component';
import {BehaviorSubject} from 'rxjs';

describe('AnomaliesComponent', () => {
  let component: AnomaliesComponent;
  let fixture: ComponentFixture<AnomaliesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AnomaliesComponent]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AnomaliesComponent);
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
