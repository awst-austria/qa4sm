import {Injectable} from '@angular/core';
import {UUID} from 'angular2-uuid';
import {interval} from 'rxjs';

export class UuidSlot {
  constructor(public unused: boolean, public uuid: string) {
  }
}

@Injectable({
  providedIn: 'root'
})
export class RndGenService {
  //Service that generates random numbers, strings etc
  private uuidPoolSize = 150;
  private uuidPool: UuidSlot[] = [];
  private timer = interval(30000);

  constructor() {
    this.timer.subscribe(value => this.fillPool());
  }

  uuid(): string {
    let localUuid;
    for (let i = 0; i < this.uuidPool.length; i++) {
      if (this.uuidPool[i].unused) {
        this.uuidPool[i].unused = false;
      }
    }
    if (localUuid == undefined) {
      localUuid = UUID.UUID();
    }
    return localUuid;
  }

  private fillPool() {
    let missingUUIDs = this.uuidPoolSize - this.uuidPool.length;
    for (let i = 0; i < missingUUIDs; i++) {
      this.uuidPool.push(new UuidSlot(false, ''));
    }

    for (let i = 0; i < this.uuidPoolSize; i++) {
      if (this.uuidPool[i].unused == false) {
        this.uuidPool[i].uuid = UUID.UUID();
        this.uuidPool[i].unused = true;
      }
    }
  }

}
