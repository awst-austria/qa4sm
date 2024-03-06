import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {LocalApiService} from '../../core/services/auth/local-api.service';
import {CountryDto} from '../../core/services/global/country.dto';
import {UserDto} from '../../core/services/auth/user.dto';
import {AuthService} from '../../core/services/auth/auth.service';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';
import {ToastService} from '../../core/services/toast/toast.service';
import {UserData} from '../../core/services/form-interfaces/UserDataForm';

@Component({
  selector: 'qa-user-form',
  templateUrl: './user-form.component.html',
  styleUrls: ['./user-form.component.scss']
})
export class UserFormComponent implements OnInit {
  userForm = this.formBuilder.group<UserData>({
    username: ['', [Validators.required, Validators.maxLength(150)]],
    password1: ['', [Validators.required]],
    password2: ['', [Validators.required]],
    email: ['', [Validators.required, Validators.email]],
    first_name: [''],
    last_name: [''],
    organisation: [''],
    country: [''],
    orcid: [''],
    terms_consent: ['', Validators.required],
    active: false,
    honeypot: [0, [Validators.required, Validators.min(100)]]
  });
  countries: CountryDto[];
  countries$: Observable<CountryDto[]>;
  selectedCountry: CountryDto;
  formErrors: any;
  sliderValues = [];

  signUpObserver = {
    next: () => this.onSignUpNext(),
    error: error => this.onSignupError(error)
  }

  UpdateObserver = {
    next: data => this.onUpdateNext(data),
    error: error => this.onUpdateError(error),
    complete: () => this.onUpdateComplete()
  }

  @Input() userData: UserDto;
  @Output() doRefresh = new EventEmitter();

  constructor(private userFormService: LocalApiService,
              private formBuilder: FormBuilder,
              private userService: AuthService,
              private router: Router,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    // this.getListOfCountries();
    this.countries$ = this.userFormService.getCountryList();
    if (this.userData) {
      this.setDefaultValues();
    }
    this.userForm.get('honeypot').valueChanges.subscribe(value => {
      this.handleSliderChange(value);
    });
  }

  onSubmit(): void {
    if (!this.userData) {
      this.userService.signUp(this.userForm.value).subscribe(this.signUpObserver);
    } else {
      this.userService.updateUser(this.userForm.value).subscribe(this.UpdateObserver);
    }
  }

  private onSignUpNext(): void {
    this.formErrors = null;
    this.router.navigate(['/signup-complete']);
  }

  private onSignupError(error): void{
    this.formErrors = error.error;
  }
  private onUpdateComplete(): void {
    this.toastService.showSuccessWithHeader('', 'User profile has been updated');
  }

  private onUpdateNext(data): void {
    this.userService.currentUser.email = data.email;
    this.userService.currentUser.first_name = data.first_name;
    this.userService.currentUser.last_name = data.last_name;
    this.userService.currentUser.organisation = data.organisation;
    this.userService.currentUser.country = data.country;
    this.userService.currentUser.orcid = data.orcid;
    this.doRefresh.emit(true);
    this.formErrors = null;
  }

  private onUpdateError(error): void {
    this.formErrors = error.error;
  }

  getListOfCountries(): void {
    this.userFormService.getCountryList().subscribe(countries => {
      this.countries = countries;
    });
  }

  setDefaultValues(): void {
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

  deactivateAccount(): void {
    const username = this.userService.currentUser.username;
    this.userService.deactivateUser(username).subscribe(
      () => {
        this.userService.currentUser = this.userService.emptyUser;
        this.userService.authenticated$.next(false);
        this.router.navigate(['/deactivate-user-complete']);
      }
    );
  }

  handleSliderChange(value: any) {
    this.sliderValues.push(value)
  }


}
