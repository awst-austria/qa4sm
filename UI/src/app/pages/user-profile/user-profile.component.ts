import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {UserDto} from '../../modules/core/services/auth/user.dto';

@Component({
    selector: 'qa-user-profile',
    templateUrl: './user-profile.component.html',
    styleUrls: ['./user-profile.component.scss'],
    standalone: false
})
export class UserProfileComponent implements OnInit {
  currentUser: UserDto;
  constructor(private authService: AuthService) {
  }

  ngOnInit(): void {
    this.currentUser = this.authService.currentUser;
  }

}
