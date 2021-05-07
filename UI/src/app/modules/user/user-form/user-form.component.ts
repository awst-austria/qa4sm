import {Component, Input, OnInit} from '@angular/core';
import {FormBuilder} from '@angular/forms';
import {LocalApiService} from '../../core/services/global/local-api.service';
import {CountryDto} from '../../core/services/global/country.dto';
import {UserDto} from '../../core/services/auth/user.dto';

@Component({
  selector: 'qa-user-form',
  templateUrl: './user-form.component.html',
  styleUrls: ['./user-form.component.scss']
})
export class UserFormComponent implements OnInit {
  userForm = this.formBuilder.group({
      username: [''],
      password: [''],
      passwordConfirmation: [''],
      email: [''],
      firstName: [''],
      lastName: [''],
      organisation: [''],
      country: [null],
      orcid: [''],
  });

  countries: CountryDto[];
  selectedCountry: CountryDto;

  @Input() userData: UserDto;

  constructor(private localApiService: LocalApiService,
              private formBuilder: FormBuilder) { }

  ngOnInit(): void {
    this.getListOfCountries();
    if (this.userData){
      this.setDefaultValues();
    }
  }

  onSubmit(): void{
    console.log('Monika');
    console.warn(this.userForm.value);
  }

  getListOfCountries(): void{
    this.localApiService.getCountryList().subscribe(countries => {
      this.countries = countries;
      this.selectedCountry = countries[0];
    });
  }

  setDefaultValues(): void{
    this.userForm.controls.username.setValue(this.userData.username);
    this.userForm.controls.email.setValue(this.userData.email);
    this.userForm.controls.firstName.setValue(this.userData.first_name);
    this.userForm.controls.lastName.setValue(this.userData.last_name);
    this.userForm.controls.organisation.setValue(this.userData.organisation);
    this.userForm.controls.orcid.setValue(this.userData.orcid);
    this.userForm.controls.country.setValue(this.userData.country);
    console.log(this.countries.find(country => country.name === this.userData.country));
    // this.selectedCountry.name = this.userData.country;
    console.log(this.userForm.controls.country);
  }

}
