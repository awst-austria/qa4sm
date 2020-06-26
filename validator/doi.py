import json
import logging

from django.conf import settings
import netCDF4
import requests


__logger = logging.getLogger(__name__)

## See https://developers.zenodo.org/#rest-api for documentation
def get_doi_for_validation(val, metadata):
    if ((not val.id) or (not val.output_file) or (not val.output_file.path) or (not val.user)):
        raise ValueError("Can't create DOI for broken validation")

    if (val.publishing_in_progress):
        raise ValueError("Publishing already in progress")

    json_header = {"Content-Type": "application/json"}
    access_param = {'access_token': settings.DOI_ACCESS_TOKEN}

    ## publishing may take a while, make sure we record the status change in the database before that
    val.is_archived = True
    val.publishing_in_progress = True
    val.save()

    try:
        ## create new entry
        r = requests.post(settings.DOI_REGISTRATION_URL, params=access_param, json={}, headers=json_header)
        __logger.debug('New DOI, create, status: ' + str(r.status_code))
        __logger.debug(r.json())

        if r.status_code != 201:
            raise RuntimeError("Could not create new DOI entry")

        deposition_id = r.json()['id']
        __logger.debug('New DOI id: ' + str(deposition_id))

        ## add metadata to new entry and get reserved DOI
        meta = {
            'upload_type': 'dataset',
            'prereserve_doi': True,
            }
        meta.update(metadata)

        data = { 'metadata': meta }
        r = requests.put(settings.DOI_REGISTRATION_URL + '/{}'.format(deposition_id), params=access_param, data=json.dumps(data), headers=json_header)
        __logger.debug('New DOI, add metadata, status: ' + str(r.status_code))
        __logger.debug(r.json())

        if r.status_code != 200:
            raise RuntimeError("Could not upload metadata to new DOI")

        reserved_doi = r.json()['metadata']['prereserve_doi']['doi']
        __logger.debug('Reserved DOI {} for deposition ID {}'.format(reserved_doi, deposition_id))

        ## put pre-reserved DOI into results file
        with netCDF4.Dataset(val.output_file.path, 'a', format='NETCDF4') as ds:
            ds.doi = settings.DOI_URL_PREFIX + reserved_doi

        ## add file to new entry
        with open(val.output_file.path, 'rb') as result_file:
            data = {'name': str(val.id) + '.nc'}
            files = {'file': result_file}
            r = requests.post(settings.DOI_REGISTRATION_URL + '/{}/files'.format(deposition_id), params=access_param, data=data, files=files)
            __logger.debug('New DOI, add files, status: ' + str(r.status_code))
            __logger.debug(r.json())

        if r.status_code != 201:
            raise RuntimeError("Could not upload result file to new DOI")

        ## PUBLISH new entry
        r = requests.post(settings.DOI_REGISTRATION_URL + '/{}/actions/publish'.format(deposition_id), params=access_param)
        __logger.debug('New DOI, publish, status: ' + str(r.status_code))
        __logger.debug(r.json())

        if r.status_code != 202:
            raise RuntimeError("Could not publish new DOI")

        val.doi = r.json()['doi']

    ## however the publication ends, make sure to signal that it's not in progress any more
    finally:
        val.publishing_in_progress = False
        val.save()
