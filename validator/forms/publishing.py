from re import search as reg_search
from re import compile as reg_compile
from re import IGNORECASE  # @UnresolvedImport

from django.conf import settings
from django.core.exceptions import ValidationError

import django.forms as forms

from api.frontend_urls import get_angular_url


def validate_orcid(orcid):
    if orcid:
        r = reg_search(settings.ORICD_REGEX, orcid)
        if not r or len(r.groups()) < 1:
            raise ValidationError('Invalid ORCID identifier.')

_KEYWORD_REGEX = reg_compile(r'\bqa4sm\b', IGNORECASE)
def validate_keywords(keywordlist):
    if not _KEYWORD_REGEX.search(keywordlist):
        raise ValidationError('Missing required keyword')

class PublishingForm(forms.Form):

    title = forms.CharField(label='Title', widget=forms.Textarea(attrs={'rows': '2'}),
                            help_text='Title of the Zenodo entry')
    description = forms.CharField(label='Description', widget=forms.Textarea(attrs={'rows': '2'}),
                                  help_text='Description of the Zenodo entry')
    keywords = forms.CharField(label='Keywords', widget=forms.Textarea(attrs={'rows': '2'}), validators=[validate_keywords],
                               help_text='Comma-separated list of keywords to make your results easily searchable; must contain keyword "qa4sm"')
    name = forms.CharField(label='Name',
                           help_text='Your name; format: Lastname, Firstnames')
    affiliation = forms.CharField(label='Affiliation', required=False,
                                  help_text='Your organisation or other affiation, optional')
    orcid = forms.CharField(label='ORCID', required=False, max_length=25, validators=[validate_orcid],
                            help_text='Your personal ORCID id, optional')

    def __init__(self, data=None, validation=None, *args, **kwargs):
        ## if no data is given, generate defaults from validation
        if (data is None) and (validation is not None):
            data = self._formdata_from_validation(validation)

        super(PublishingForm, self).__init__(data, *args, **kwargs)

    def _validation_url(self, val_id):
        return settings.SITE_URL + get_angular_url('result', val_id)

    def _formdata_from_validation(self, validation):
            title = "Validation of " + (" vs ".join(['{} {}'.format(dc.dataset.pretty_name, dc.version.pretty_name) for dc in validation.dataset_configurations.all()]))

            description = 'QA4SM validation: ' + (" vs ".join(['{} {}'.format(dc.dataset.pretty_name, dc.version.pretty_name) for dc in validation.dataset_configurations.all()])) + '. URL: ' + self._validation_url(validation.id) + '. Produced on QA4SM (' + settings.SITE_URL + ')'

            dataset_names = set([dc.dataset.pretty_name for dc in validation.dataset_configurations.all()])
            keywords = ['soil moisture', 'validation', 'qa4sm',]
            keywords.extend(dataset_names)

            if validation.user.first_name and validation.user.last_name:
                name = '{}, {}'.format(validation.user.last_name, validation.user.first_name)
            elif validation.user.first_name:
                name = validation.user.first_name
            elif validation.user.last_name:
                name = validation.user.last_name
            else:
                name = 'Anonymous'

            affiliation = validation.user.organisation
            orcid = validation.user.orcid

            data = {
                'title': title,
                'description': description,
                'keywords': ', '.join(keywords),
                'name': name,
                'affiliation': affiliation,
                'orcid': orcid,
                }

            return data

    @property
    def pub_metadata(self):
        if not self.is_valid():
            raise Exception("Invalid form content, unable to render metadata")

        keyword_delimiter = reg_compile(r"[\s]*,[\s]*")
        keywords = []

        if self.cleaned_data['keywords']:
            k = keyword_delimiter.split(self.cleaned_data['keywords'])
            keywords.extend(k)

        creator = {'name': self.cleaned_data['name'],}

        if self.cleaned_data['affiliation']:
            creator['affiliation'] = self.cleaned_data['affiliation']

        if self.cleaned_data['orcid']:
            creator['orcid'] = self.cleaned_data['orcid']

        data = {
            'title': self.cleaned_data['title'],
            'description': self.cleaned_data['description'],
            'keywords': keywords,
            'creators': [creator],
            }

        return data
