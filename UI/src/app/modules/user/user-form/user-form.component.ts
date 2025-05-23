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
import {CustomHttpError} from '../../core/services/global/http-error.service';
import {SettingsService} from "../../core/services/global/settings.service";
import { ConfirmationService } from 'primeng/api';

@Component({
  selector: 'qa-user-form',
  templateUrl: './user-form.component.html',
  styleUrls: ['./user-form.component.scss'],
  providers: [ConfirmationService]
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
  maintenanceMode = false;

  signUpObserver = {
    next: () => this.onSignUpNext(),
    error: (error: CustomHttpError) => this.onFormSubmitError(error)
  }

  UpdateObserver = {
    next: (data: UserData) => this.onUpdateNext(data),
    error: (error: CustomHttpError) => this.onFormSubmitError(error),
    complete: () => this.onUpdateComplete()
  }

  deactivateObserver = {
    next: () => this.deactivateAccountNext(),
    error: () => this.deactivateAccountError()
  }

  @Input() userData: UserDto;
  @Output() doRefresh = new EventEmitter();

  constructor(private userFormService: LocalApiService,
              private formBuilder: FormBuilder,
              private userService: AuthService,
              private router: Router,
              private toastService: ToastService,
              private settingsService: SettingsService,
              private confirmationService: ConfirmationService) {
  }

  ngOnInit(): void {
    this.countries$ = this.userFormService.getCountryList();
    if (this.userData) {
      this.setDefaultValues();
    }
    this.userForm.get('honeypot').valueChanges.subscribe(value => {
      this.handleSliderChange(value);
    });
    this.settingsService.getAllSettings().subscribe(setting => {
      this.maintenanceMode = setting[0].maintenance_mode;
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
    this.router.navigate(['/signup-complete']).then(
      () => this.toastService.showSuccess('Data submitted successfully.')
    );
  }

  private onUpdateComplete(): void {
    this.toastService.showSuccess('User profile has been updated');
  }

  private onUpdateNext(data: UserData): void {
    Object.assign(this.userService.currentUser, data)
    this.doRefresh.emit(true);
    this.formErrors = null;
  }

  private onFormSubmitError(error: CustomHttpError): void {
    this.formErrors = error.form;
    this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message);
  }


  confirmRequestToken() {
    this.confirmationService.confirm({
      key: 'apiTokenConfirm',
      message: 'This API token can be used to submit validation jobs via API request. Your our token request will be reviewed by admins. Once granted the token will be displayed on your user profile. \n Information on how to use the token is provided in the user manual. Please only confirm if you do intend to use the QA4SM service via API.',
      header: 'Confirm Request',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Confirm',
      rejectLabel: 'Cancel',
      accept: () => {
        this.requestApiToken();
      }
    });
  }

  requestApiToken() {
    this.userService.requestApiToken().subscribe(
        response => {
            this.toastService.showSuccess('API token request has been sent to administrators');
        },
        error => {
            this.toastService.showErrorWithHeader('Failed to request API token', error.message);
        }
    );
}

  setDefaultValues(): void {
    this.userForm.patchValue(this.userData)
    this.userForm.controls.username.disable();
    this.userForm.controls.password1.disable();
    this.userForm.controls.password2.disable();
    this.userForm.controls.terms_consent.setValue(true);
  }

  deactivateAccount(): void {
    this.userService.deactivateUser(this.userService.currentUser.username)
      .subscribe(this.deactivateObserver);
  }

  deactivateAccountNext(): void {
    this.userService.currentUser = this.userService.emptyUser;
    this.userService.authenticated.next(false);
    this.router.navigate(['/deactivate-user-complete'])
      .then(
        () => this.toastService.showSuccess('Your request has been sent.')
      );
  }

  deactivateAccountError(): void {
    this.toastService.showErrorWithHeader('Something went wrong', 'Your request could not be sent. ' +
      'Please try again later, or contact our support team.')
  }

  handleSliderChange(value: any) {
    this.sliderValues.push(value)
  }

  redirectToSetPassword(){
    this.router.navigate(['/set-password'])
  }

}
