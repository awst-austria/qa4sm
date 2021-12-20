import {Component, Input, OnInit} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {LocalApiService} from '../../core/services/auth/local-api.service';
import {CountryDto} from '../../core/services/global/country.dto';
import {UserDto} from '../../core/services/auth/user.dto';
import {AuthService} from '../../core/services/auth/auth.service';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';
import {ToastService} from '../../core/services/toast/toast.service';

@Component({
  selector: 'qa-user-form',
  templateUrl: './user-form.component.html',
  styleUrls: ['./user-form.component.scss']
})
export class UserFormComponent implements OnInit {
  userForm = this.formBuilder.group({
      username: ['', [Validators.required, Validators.maxLength(150)]],
      password1: ['', [Validators.required]],
      password2: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      first_name: [''],
      last_name: [''],
      organisation: [''],
      country: [''],
      orcid: [''],
      terms_consent: ['', Validators.required]
  });
  countries: CountryDto[];
  countries$: Observable<CountryDto[]>;
  selectedCountry: CountryDto;
  formErrors: any;

  @Input() userData: UserDto;

  constructor(private userFormService: LocalApiService,
              private formBuilder: FormBuilder,
              private userService: AuthService,
              private router: Router,
              private toastService: ToastService) { }

  ngOnInit(): void {
    // this.getListOfCountries();
    this.countries$ = this.userFormService.getCountryList();
    if (this.userData){
      this.setDefaultValues();
    }
  }

  onSubmit(): void{
    if (!this.userData){
      this.userService.signUp(this.userForm.value).subscribe(
        () => {
          this.router.navigate(['/signup-complete']);
        },
        error => {
          this.formErrors = error.error;
        });
    } else {
      this.userService.updateUser(this.userForm.value).subscribe(
        data => {
          this.userService.currentUser.email = data.email;
          this.userService.currentUser.first_name = data.first_name;
          this.userService.currentUser.last_name = data.last_name;
          this.userService.currentUser.organisation = data.organisation;
          this.userService.currentUser.country = data.country;
          this.userService.currentUser.orcid = data.orcid;
        },
        error => {
          this.formErrors = error.error;
        },
        () => {
          this.toastService.showSuccessWithHeader('', 'User profile has been updated');
        }
      );
    }
  }

  getListOfCountries(): void{
    this.userFormService.getCountryList().subscribe(countries => {
      this.countries = countries;
    });
  }

  setDefaultValues(): void{
    this.userForm.controls.username.setValue(this.userData.username);
    this.userForm.controls.username.disable();
    this.userForm.controls.email.setValue(this.userData.email);
    this.userForm.controls.password1.clearValidators();
    this.userForm.controls.password2.clearValidators();
    this.userForm.controls.first_name.setValue(this.userData.first_name);
    this.userForm.controls.last_name.setValue(this.userData.last_name);
    this.userForm.controls.organisation.setValue(this.userData.organisation);
    this.userForm.controls.country.setValue(this.userData.country);
    this.userForm.controls.orcid.setValue(this.userData.orcid);
    this.userForm.controls.terms_consent.setValue(true);
  }

  deactivateAccount(): void{
    const username = this.userService.currentUser.username;
    this.userService.deactivateUser(username).subscribe(
      () => {
        this.router.navigate(['/deactivate-user-complete']);
      }
    );
  }

}
