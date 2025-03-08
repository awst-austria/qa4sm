import {WritableSignal} from "@angular/core";

type FilterType = 'string' | 'dropdown' | 'multi-select' | 'single-select' | 'date' ;

export interface FilterConfig {
  backendName: string;
  label: string;
  optionPlaceHolder: string;
  type: FilterType;
  options?: string[];
  value?: string;
  selectedOptions?: WritableSignal<string[]>;
}
