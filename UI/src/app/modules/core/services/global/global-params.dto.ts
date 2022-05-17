export class GlobalParamsDto {

  constructor(public admin_mail: string,
              public doi_prefix: string,
              public site_url: string,
              public app_version: string,
              public expiry_period: string,
              public warning_period: string,
              public temporal_matching_default: number
              ) {
  }
}
