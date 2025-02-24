
type FilterType = 'string-input' | 'dropdown' | 'multi-select' | 'single-select' | 'date-input' | 'date-range' | 'dataset';

export interface FilterPayload {
  [key: string]: string[] | string | null;
}

export interface FilterConfig {
  name: string;
  type: FilterType;
  value: string[];
  validationFn: (value: any) => boolean;
  formatValuesFn: (value: any) => string[];
  backendField: string; // Field name used in backend query
  options?: string[];
}
