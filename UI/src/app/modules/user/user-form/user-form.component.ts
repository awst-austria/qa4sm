import {Component, Input, OnInit} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {LocalApiService} from '../../core/services/global/local-api.service';
import {CountryDto} from '../../core/services/global/country.dto';
import {UserDto} from '../../core/services/auth/user.dto';
import {AuthService} from '../../core/services/auth/auth.service';
import {Observable} from 'rxjs';

@Component({
  selector: 'qa-user-form',
  templateUrl: './user-form.component.html',
  styleUrls: ['./user-form.component.scss']
})
export class UserFormComponent implements OnInit {
  userForm = this.formBuilder.group({
      username: ['', Validators.required],
      password: [''],
      password2: [''],
      email: [''],
      first_name: [''],
      last_name: [''],
      organisation: [''],
      country: [null],
      orcid: [''],
  });

  countries: CountryDto[];
  countries$: Observable<CountryDto[]>;
  selectedCountry: CountryDto;

  @Input() userData: UserDto;

  constructor(private localApiService: LocalApiService,
              private formBuilder: FormBuilder,
              private userService: AuthService) { }

  ngOnInit(): void {
    // this.getListOfCountries();
    this.countries$ = this.localApiService.getCountryList();
    if (this.userData){
      this.setDefaultValues();
    }
  }

  onSubmit(): void{
    if (!this.userData){
      this.userService.signUp(this.userForm.value);
    } else {
      this.userService.updateUser(this.userForm.value);
    }
  }

  getListOfCountries(): void{
    this.localApiService.getCountryList().subscribe(countries => {
      this.countries = countries;
    });
  }

  setDefaultValues(): void{
    this.userForm.controls.username.setValue(this.userData.username);
    this.userForm.controls.email.setValue(this.userData.email);
    this.userForm.controls.first_name.setValue(this.userData.first_name);
    this.userForm.controls.last_name.setValue(this.userData.last_name);
    this.userForm.controls.organisation.setValue(this.userData.organisation);
    this.userForm.controls.country.setValue(this.userData.country);
    this.userForm.controls.orcid.setValue(this.userData.orcid);
  }

  deactivateAccount(): void{
    const username = this.userService.currentUser.username;
    this.userService.deactivateUser(username);
  }

}
