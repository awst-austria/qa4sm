export class SettingsDto {
  constructor(public id: number,
              public maintenance_mode: boolean,
              public potential_maintenance: boolean,
              public news: string,
              public potential_maintenance_description: string,
              public sum_link: string,
              public feed_link: string
              ) {
  }
}
