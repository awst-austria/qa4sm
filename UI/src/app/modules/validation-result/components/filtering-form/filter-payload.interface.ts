import {Observable} from "rxjs";

type FilterType = 'string' | 'dropdown' | 'multi-select' | 'single-select' | 'date' ;

export interface FilterPayload {
  [key: string]: string[] | string | null;
}

export interface FilterConfig {
  name: string;
  label: string;
  optionPlaceHolder: string;
  type: FilterType;
  validationFn?: (value: any) => boolean;
  formatValuesFn?: (value: any) => string[];
  options?: string[] | Observable<string[]>;
  value?: string;
  selectedOptions?: string[];
  backendQuery: string;
}
