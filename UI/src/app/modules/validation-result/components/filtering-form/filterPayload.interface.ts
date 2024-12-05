export interface FilterPayload {
    statuses: string[];
    name: string | null;
    spatialRef: string[];
    temporalRef: string[];
    scalingRef: string[];
  }