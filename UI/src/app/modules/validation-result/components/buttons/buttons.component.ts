import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {HttpClient} from '@angular/common/http';
import {Router} from '@angular/router';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {saveAs} from 'file-saver';


@Component({
  selector: 'qa-buttons',
  templateUrl: './buttons.component.html',
  styleUrls: ['./buttons.component.scss']
})

export class ButtonsComponent implements OnInit {

  @Input() validationRun: ValidationrunDto;
  @Input() published: boolean;
  @Input() validationList: boolean;
  @Input() tracked: boolean;

  faIcons = {faArchive: fas.faArchive,
    faStop: fas.faStop,
    faFileDownload: fas.faFileDownload,
    faRedo: fas.faRedo};

  isOwner = true;
  isCurrentUser = true;
  isCopied = true;
  status: string;
  graphicsFileName = 'graphs.zip';


  constructor(private httpClient: HttpClient,
              private router: Router,
              private validationService: ValidationrunService) { }

  ngOnInit(): void {
  }

  basicOnclick(validation: ValidationrunDto): void{
  //  I'll remove this one, now it's just a function to check if buttons work
    console.log(validation.id);
  }

  reloadMyValidations(): void{
    const targetUrl = '/my-validations';
    this.router.routeReuseStrategy.shouldReuseRoute = () => false;
    this.router.onSameUrlNavigation = 'reload';
    this.router.navigate([targetUrl]);
  }


  deleteValidation(validationId: string): void{
    this.validationService.deleteValidation(validationId);
    this.reloadMyValidations();

  }

  stopValidation(validationId: string): void{
    this.validationService.stopValidation(validationId);
    this.reloadMyValidations();
  }

  archiveResults(validationId: string, archive: boolean): void{
    this.validationService.archiveResults(validationId, archive);
    window.location.reload();
  }

  extendResults(validationId: string): void{
    this.validationService.extendResults(validationId);
  }

  downloadResultFile(fileUrl: string, fileName: string): void{
    this.validationService.downloadResultFile(fileUrl)
      .subscribe(blob => saveAs(blob, fileName));
  }

}
