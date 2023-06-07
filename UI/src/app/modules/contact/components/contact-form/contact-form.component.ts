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
  });

  constructor(private userDatasetService: UserDatasetsService,
              private formBuilder: FormBuilder,
              private toastService: ToastService,
              public authService: AuthService) {
  }

  public onSubmit(): void{
    console.log(this.contactForm);
    this.authService.sendSupportRequest(this.contactForm.value).subscribe(data => {
      this.toastService.showSuccess('Your message has been sent successfully. We will reach out to you within 3 working days.')
    })
  }

}
