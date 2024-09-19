import {ValidationRunMetricConfigDto} from '../../../../pages/validate/service/validation-run-config-dto';

export class MetricModel {
  constructor(public name: string,
              public description: string,
              public helperText: string,
              public value: boolean,
              public switchOffIfDisabled: boolean,
              public isDisabled: () => boolean,
              public onChange?: (newValue: boolean) => void) {
    // Computed signal that automatically disables the value if enabledCallback is false
  }

  triggerDisabledCheck(automaticallySwitchOff): boolean {
    const disabled = this.isDisabled();
    if (disabled && automaticallySwitchOff) {
      this.value = false;
    }
      return disabled;
  }

  // Method to trigger the onChange callback when the value changes
  triggerOnChange(newValue: boolean): void {
    if (this.onChange) {
      this.onChange(newValue); // Call the callback function
    }
  }

  toValidationRunMetricDto(): ValidationRunMetricConfigDto {
    return {id: this.name, value: this.value} as ValidationRunMetricConfigDto;
  }
}
