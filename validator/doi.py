import json
import logging

from django.conf import settings
import requests


__logger = logging.getLogger(__name__)

def get_doi_for_validation(val):
    if ((not val.id) or (not val.output_file.path) or (not val.user)):
        raise Exception("Can't create DOI for broken validation")

    json_header = {"Content-Type": "application/json"}
    access_param = {'access_token': settings.DOI_ACCESS_TOKEN}

    ## create new entry
    r = requests.post(settings.DOI_REGISTRATION_URL, params=access_param, json={}, headers=json_header)
    __logger.debug('New DOI, create, status: ' + str(r.status_code))
    __logger.debug(r.json())

    if r.status_code != 201:
        raise Exception("Could not create new DOI entry")

    deposition_id = r.json()['id']
    __logger.debug('New DOI id: ' + str(deposition_id))

    ## add file to new entry
    with open(val.output_file.path, 'rb') as result_file:
        data = {'name': 'results.nc'}
        files = {'file': result_file}
        r = requests.post(settings.DOI_REGISTRATION_URL + '/{}/files'.format(deposition_id), params=access_param, data=data, files=files)
        __logger.debug('New DOI, add files, status: ' + str(r.status_code))
        __logger.debug(r.json())

    if r.status_code != 201:
        raise Exception("Could not upload result file to new DOI")

    ## add metadata to new entry
    title = "Validation of  " + (" vs \n".join(['{} {}'.format(dc.dataset.pretty_name, dc.version.pretty_name) for dc in val.dataset_configurations.all()]))

    if val.user.first_name and val.user.last_name:
        name = '{}, {}'.format(val.user.last_name, val.user.first_name)
    elif val.user.first_name:
        name = val.user.first_name
    elif val.user.last_name:
        name = val.user.last_name
    else:
        name = 'Anonymous'

    creator = {'name': name,}

    if val.user.organisation:
        creator['affiliation'] = val.user.organisation

    if val.user.orcid:
        creator['orcid'] = val.user.orcid

    keywords = ['soil moisture', 'validation', 'qa4sm', ]
    dataset_names = set([dc.dataset.pretty_name for dc in val.dataset_configurations.all()])
    for dn in dataset_names:
        keywords.append(dn)

    data = {
        'metadata': {
            'title': title,
            'upload_type': 'dataset',
            'description': title + ', run on QA4SM (' + settings.SITE_URL + ')',
            'keywords' : keywords,
            'creators': [creator]
            }
        }
    r = requests.put(settings.DOI_REGISTRATION_URL + '/{}'.format(deposition_id), params=access_param, data=json.dumps(data), headers=json_header)
    __logger.debug('New DOI, add metadata, status: ' + str(r.status_code))
    __logger.debug(r.json())

    if r.status_code != 200:
        raise Exception("Could not upload metadata to new DOI")

    ## PUBLISH new entry
    r = requests.post(settings.DOI_REGISTRATION_URL + '/{}/actions/publish'.format(deposition_id), params=access_param)
    __logger.debug('New DOI, publish, status: ' + str(r.status_code))
    __logger.debug(r.json())

    if r.status_code != 202:
        raise Exception("Could not publish new DOI")

    val.doi = r.json()['doi']
    val.save()
