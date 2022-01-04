import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.scss']
})
export class UserProfileComponent implements OnInit {

  constructor(private authService: AuthService) {
  }

  ngOnInit(): void {
  }

  getUsername(): string {
    return this.authService.currentUser.username;
  }

}
