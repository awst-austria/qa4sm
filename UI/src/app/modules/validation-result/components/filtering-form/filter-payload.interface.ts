import {Observable} from "rxjs";

type FilterType = 'string' | 'dropdown' | 'multi-select' | 'single-select' | 'date' ;

export interface FilterPayload {
  [key: string]: string[] | string | null;
}

export interface FilterConfig {
  name: string;
  displayName: string;
  type: FilterType;
  value: string[];
  validationFn: (value: any) => boolean;
  formatValuesFn: (value: any) => string[];
  options?: string[] | Observable<string[]>;
}
