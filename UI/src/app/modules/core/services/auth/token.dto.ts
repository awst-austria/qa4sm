export interface TokenResponse {
  readonly token: string;
  readonly expiresAt: string;
  readonly isValid: boolean;
  readonly status: 'pending' | 'approved' | 'rejected';
  readonly userId: number;
}

export interface TokenRequest {
  readonly userId: number;
  readonly timestamp: string;   
}
