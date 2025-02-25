export interface MultipleValidationAction {
  active: boolean;
  action: string;
  allSelected: boolean;
  selectedValidationIds: string[];
}

// Define the default state as a constant
export const DEFAULT_VALIDATION_ACTION_STATE: MultipleValidationAction = {
  active: false,
  action: null,
  allSelected: false,
  selectedValidationIds: []
};

// Define a function in case you need a fresh copy each time
export function getDefaultValidationActionState(): MultipleValidationAction {
  return {...DEFAULT_VALIDATION_ACTION_STATE};
}
