import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';

@Component({
  selector: 'qa-password-reset',
  templateUrl: './password-reset.component.html',
  styleUrls: ['./password-reset.component.scss']
})
export class PasswordResetComponent implements OnInit {


  resetPasswordForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
  });
  constructor() { }

  ngOnInit(): void {
  }

  onSubmit(): void{
    console.log('reset my password');
  }
}
