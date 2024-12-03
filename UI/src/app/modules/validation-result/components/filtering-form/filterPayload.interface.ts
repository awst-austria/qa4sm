export interface FilterPayload {
  name: string; // Filter name (e.g., 'Date', 'Name', 'Dataset')
  type: 'checkbox' | 'dropdown' | 'input' | 'calendar'; // Filter input type
  label: string;
  options?: { label: string; value: any }[]; // Options for dropdown or checkboxes
  value?: any; // Current value of the filter
}
