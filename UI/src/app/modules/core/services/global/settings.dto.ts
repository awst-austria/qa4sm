export class SettingsDto {
  constructor(public id: number,
              public maintenance_mode : boolean,
              public news: string,
              public sum_link: string,
              public feed_link: string
              ) {
  }
}
