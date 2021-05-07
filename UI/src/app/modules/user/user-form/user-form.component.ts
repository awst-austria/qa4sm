import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup} from '@angular/forms';
import {LocalApiService} from '../../core/services/global/local-api.service';
import {CountryDto} from '../../core/services/global/country.dto';

@Component({
  selector: 'qa-user-form',
  templateUrl: './user-form.component.html',
  styleUrls: ['./user-form.component.scss']
})
export class UserFormComponent implements OnInit {
  userForm = new FormGroup({
    username: new FormControl(''),
    password: new FormControl(''),
    passwordConfirmation: new FormControl(''),
    email: new FormControl(''),
    firstName: new FormControl(''),
    lastName: new FormControl(''),
    organisation: new FormControl(''),
    country: new FormControl(''),
    orcid: new FormControl(''),
  });
  countries: CountryDto[];
  selectedCountry: CountryDto;

  constructor(private localApiService: LocalApiService) { }

  ngOnInit(): void {
    this.getListOfCountries();
  }

  onSubmit(): void{
    console.log('Monika');
  }

  getListOfCountries(): void{
    this.localApiService.getCountryList().subscribe(countries => {
      console.log(countries);
      this.countries = countries;
      this.selectedCountry = countries[0];
    });
  }

}
