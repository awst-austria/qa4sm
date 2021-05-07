import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {UserDto} from '../../modules/core/services/auth/user.dto';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.scss']
})
export class UserProfileComponent implements OnInit {
  currentUser: UserDto;
  constructor(private authService: AuthService) {
  }

  ngOnInit(): void {
    this.currentUser = this.authService.currentUser;
  }

  // getUsername(): string {
  //   return this.authService.currentUser.username;
  // }

}
