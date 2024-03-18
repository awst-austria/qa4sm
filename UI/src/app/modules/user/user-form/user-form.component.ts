import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {LocalApiService} from '../../core/services/auth/local-api.service';
import {CountryDto} from '../../core/services/global/country.dto';
import {UserDto} from '../../core/services/auth/user.dto';
import {AuthService} from '../../core/services/auth/auth.service';
import {EMPTY, Observable} from 'rxjs';
import {Router} from '@angular/router';
import {ToastService} from '../../core/services/toast/toast.service';
import {UserData} from '../../core/services/form-interfaces/UserDataForm';
import {catchError} from 'rxjs/operators';
import {CustomHttpError} from '../../core/services/global/http-error.service';

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

  countries$: Observable<CountryDto[]>;
  selectedCountry: CountryDto;
  formErrors: any;
  sliderValues = [];

  updateObserver = {
    next: (data: UserData) => this.onUpdateNext(data),
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
      this.userService.signUp(this.userForm.value)
        .pipe(
          catchError(error => this.onFormSubmitErrorError(error))
        )
        .subscribe(() => this.onSignUpNext());
    } else {
      this.userService.updateUser(this.userForm.value)
        .pipe(
          catchError(error => this.onFormSubmitErrorError(error))
        )
        .subscribe(this.updateObserver);
    }
  }

  private onSignUpNext(): void {
    this.formErrors = null;
    this.router.navigate(['/signup-complete'])
      .then(() => this.toastService.showSuccess('Data submitted successfully.'));
  }

  private onUpdateComplete(): void {
    this.toastService.showSuccess('Your profile has been updated');
  }

  private onUpdateNext(data: UserData): void {
    Object.assign(this.userService.currentUser, data)
    this.doRefresh.emit(true);
    this.formErrors = null;
  }

  private onFormSubmitErrorError(error: CustomHttpError): Observable<never> {
    this.formErrors = error.errorMessage.form;
    this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message);
    return EMPTY
  }

  setDefaultValues(): void {
    this.userForm.patchValue(this.userData)
    this.userForm.controls.username.disable();
    this.userForm.controls.terms_consent.setValue(true);
  }

  deactivateAccount(): void {
    this.userService.deactivateUser(this.userService.currentUser.username)
      .subscribe(
      () => {
        this.userService.currentUser = this.userService.emptyUser;
        this.userService.authenticated.next(false);
        this.router.navigate(['/deactivate-user-complete']);
      }
    );
  }

  handleSliderChange(value: any) {
    this.sliderValues.push(value)
  }


}
