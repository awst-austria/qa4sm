export interface UserDto {
  username: string;
  first_name: string;
  id: number;
  copied_runs: string[];
  email: string;
  last_name: string;
  organisation: string;
  country: string;
  orcid: string;
  space_limit: string;
  space_limit_value: number;
  space_left: number;
  is_staff: boolean,
  is_superuser: boolean,
  auth_token?: string
}
