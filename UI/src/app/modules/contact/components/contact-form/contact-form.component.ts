import {Component} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {UserDatasetsService} from '../../../user-datasets/services/user-datasets.service';
import {ToastService} from '../../../core/services/toast/toast.service';
import {AuthService} from '../../../core/services/auth/auth.service';
import {ContactForm} from '../../../core/services/form-interfaces/contact-form';

@Component({
  selector: 'qa-contact-form',
  templateUrl: './contact-form.component.html',
  styleUrls: ['./contact-form.component.scss']
})
export class ContactFormComponent {

  contactForm = this.formBuilder.group<ContactForm>({
    name: ['', [Validators.required, Validators.maxLength(150)]],
    email: ['', [Validators.required, Validators.email]],
    content: ['', [Validators.required]],
    send_copy_to_user: false,
    active: false,
    honeypot: [0, [Validators.required, Validators.min(100)]]
  });

  formObserver = {
    next: next => this.onSubmitNext(),
    error: error => this.onSubmitError(error),
    complete: () => this.onSubmitComplete()
  };

  constructor(private userDatasetService: UserDatasetsService,
              private formBuilder: FormBuilder,
              private toastService: ToastService,
              public authService: AuthService) {
  }

  public onSubmit(): void {
    this.authService.sendSupportRequest(this.contactForm.value).subscribe(this.formObserver)
  }

  onSubmitNext(): void {
    this.toastService.showSuccess('Your message has been sent successfully. We will reach out to you within 3 working days.');
  }
  onSubmitError(error): void{
    this.toastService.showErrorWithHeader('We could not send your message', error.error.message);
  }
  onSubmitComplete(): void{
    this.contactForm.reset({});
  }

}
