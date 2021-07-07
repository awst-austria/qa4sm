export class PublishingFormDto{
  constructor(public title: string,
              public description: string,
              public keywords: string,
              public name: string,
              public affiliation: string,
              public ORCID: string) {
  }
}
