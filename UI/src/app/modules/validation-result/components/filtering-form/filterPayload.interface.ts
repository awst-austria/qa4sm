export interface FilterPayload {
    statuses: string[];
    name: string | null;
    selectedDates: [Date, Date];
    prettyName: string;
    spatialReference: boolean;
    temporalReference: boolean;
    scalingReference: boolean;
  }