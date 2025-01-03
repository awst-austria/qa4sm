
type FilterType = 'string-input' | 'dropdown' | 'multi-select' | 'single-select' | 'date-range' | 'dataset';

export interface FilterPayload {
  [key: string]: string[] | string | null;
}

export interface FilterConfig {
  name: string;
  type: FilterType;
  options?: string[];
  validationFn: (value: any) => boolean;
  formatValuesFn: (value: any) => string[];
  backendField: string; // Field name used in backend query
  isArray?: boolean;    // Whether backend expects array of values
}