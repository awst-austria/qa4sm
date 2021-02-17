export interface DatasetDto {
  id: number;
  short_name: string;
  pretty_name: string;
  help_text: string;
  storage_path: string;
  detailed_description: string;
  source_reference: string;
  citation: string;
  is_only_reference: boolean;
  versions: number[];
  variables: number[];
  filters: number[];
}
