import {Component, HostListener, Input, OnInit} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {HttpParams} from '@angular/common/http';
import {BehaviorSubject} from 'rxjs';

@Component({
    selector: 'qa-validation-page-paginated',
    templateUrl: './validation-page-paginated.component.html',
    styleUrls: ['./validation-page-paginated.component.scss']
})
export class ValidationPagePaginatedComponent implements OnInit {
    @Input() published: boolean;

    commonClasses = 'col-12 md:col-10 lg:col-10 xl:col-8  xl:col-offset-2 '
    myValClasses = this.commonClasses + 'col-offset-4  md:col-offset-3  lg:col-offset-2'
    publishedValClasses = this.commonClasses + 'md:col-offset-1 lg:col-offset-1'

    validations: ValidationrunDto[] = [];
    maxNumberOfPages: number;
    currentPage = 1;
    limit = 10;
    offset = 0;
    order = '-start_time';
    selectionActive$ = new BehaviorSubject(false);
    selectedValidations$: BehaviorSubject<any> = new BehaviorSubject<any>([]);


    isLoading: boolean = false;
    endOfPage: boolean = false;

    constructor(private validationrunService: ValidationrunService) {
    }

    ngOnInit(): void {
      console.log(window.innerWidth)
        this.getValidationsAndItsNumber(this.published);
        this.validationrunService.doRefresh.subscribe(value => {
            if (value && value !== 'page') {
                this.updateData(value);
            } else if (value && value === 'page') {
                this.refreshPage();
            }
        });
    }

    @HostListener('window:scroll', ['$event'])
    onScroll() {
        const windowHeight = 'innerHeight' in window ? window.innerHeight : document.documentElement.offsetHeight;
        const docHeight = document.documentElement.scrollHeight
        const windowBottom = windowHeight + window.scrollY;

        if (windowBottom >= docHeight - 1 && !this.isLoading && !this.endOfPage) {
            this.currentPage++;
            this.offset = (this.currentPage - 1) * this.limit;
            this.getValidationsAndItsNumber(this.published);
        }
    }

    getValidationsAndItsNumber(published: boolean): void {
        this.isLoading = true;
        const parameters = new HttpParams().set('offset', String(this.offset)).set('limit', String(this.limit))
            .set('order', String(this.order));
        if (!published) {
            this.validationrunService.getMyValidationruns(parameters).subscribe(
                response => {
                    this.handleFetchedValidations(response)
                });
        } else {
            this.validationrunService.getPublishedValidationruns(parameters).subscribe(
                response => {
                    this.handleFetchedValidations(response);
                });
        }
    }

    handleFetchedValidations(serverResponse: { validations: ValidationrunDto[]; length: number; }): void {
        const {validations, length} = serverResponse;
        if (!this.maxNumberOfPages) {
            this.maxNumberOfPages = Math.ceil(length / this.limit);
        }
        if (validations.length) {
            this.validations = this.validations.concat(validations);

            if (this.currentPage > this.maxNumberOfPages) {
                this.endOfPage = true;
            }
        } else {
            this.endOfPage = true;
        }

        this.isLoading = false;
    }

    getOrder(order): void {
        this.order = order;
        this.getValidationsAndItsNumber(this.published);
    }

    updateData(validationId: string): void {
        const indexOfValidation = this.validations.findIndex(validation => validation.id === validationId);
        this.validationrunService.getValidationRunById(validationId).subscribe(data => {
            this.validations[indexOfValidation] = data;
        });
    }

    refreshPage(): void {
        const parameters = new HttpParams().set('offset', String(this.offset)).set('limit', String(this.limit))
            .set('order', String(this.order));
        this.validationrunService.getMyValidationruns(parameters).subscribe(
            response => {
                const {validations, length} = response;
                this.validations = validations;
                // this.numberOfValidations = length;
            });
    }

    handleMultipleSelection(event): void {
        this.selectionActive$.next(event.activate)
        this.selectedValidations$.next(event.selected.value)
    }

    updateSelectedValidations(checked: string[], id: string): void {
        let selectedValidations = this.selectedValidations$.getValue();
        if (checked.includes(id)) {
            selectedValidations = [...selectedValidations, id];
        } else {
            selectedValidations = selectedValidations.filter(selectedId => selectedId !== id);
        }
        this.selectedValidations$.next(selectedValidations)
    }

}
