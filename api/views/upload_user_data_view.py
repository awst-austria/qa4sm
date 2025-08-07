import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from django.utils import timezone
from django.conf import settings
from pathlib import Path

from api.views.auxiliary_functions import get_fields_as_list
from validator.models import UserDatasetFile, DatasetVersion, DataVariable, Dataset, DataManagementGroup
from api.variable_and_field_names import *
import logging
from validator.validation.globals import USER_DATASET_MIN_ID, USER_DATASET_VERSION_MIN_ID, USER_DATASET_VARIABLE_MIN_ID
from multiprocessing.context import Process

from validator.validation.util import has_csv_in_zip
from validator.validation.user_data_processing import user_data_preprocessing, run_upload_format_check
from django.db import transaction, connections

__logger = logging.getLogger(__name__)


def create_variable_entry(variable_name,
                          variable_pretty_name,
                          dataset_name,
                          user,
                          variable_unit=None,
                          max_value=None,
                          min_value=None):
    current_max_id = DataVariable.objects.all().last(
    ).id if DataVariable.objects.all().last() else 0
    new_variable_data = {
        'short_name': variable_name,
        'pretty_name': variable_pretty_name,
        'help_text':
        f'Variable {variable_name} of dataset {dataset_name} provided by  user {user}.',
        'min_value': max_value,
        'max_value': min_value,
        'unit': variable_unit if variable_unit else 'n.a.'
    }
    variable_serializer = DatasetVariableSerializer(data=new_variable_data)
    if variable_serializer.is_valid():
        new_variable = variable_serializer.save()
        new_variable_id = new_variable.id
        # need to leave some id spots for our datasets, to avoid overriding users' entries
        if new_variable_id < USER_DATASET_VARIABLE_MIN_ID:
            new_variable.id = USER_DATASET_VARIABLE_MIN_ID if current_max_id < USER_DATASET_VARIABLE_MIN_ID \
                else current_max_id + 1
            new_variable.save()
            # need to remove this one, otherwise it will be duplicated
            DataVariable.objects.get(id=new_variable_id).delete()
        return new_variable
    else:
        raise Exception(variable_serializer.errors)


def create_version_entry(version_name, version_pretty_name,
                         dataset_pretty_name, user, variable):
    current_max_id = DatasetVersion.objects.all().last(
    ).id if DatasetVersion.objects.all().last() else 0
    new_version_data = {
        "short_name": version_name,
        "pretty_name": version_pretty_name,
        "help_text":
        f'Version {version_pretty_name} of dataset {dataset_pretty_name} provided by user {user}.',
        "time_range_start": None,
        "time_range_end": None,
        "geographical_range": None,
        "filters": [],
        'variables': [variable.pk]
    }

    version_serializer = DatasetVersionSerializer(data=new_version_data)
    if version_serializer.is_valid():
        new_version = version_serializer.save()
        new_version_id = new_version.id
        # need to leave some id spots for our datasets, to avoid overriding users' entries
        if new_version_id < USER_DATASET_VERSION_MIN_ID:
            new_version.id = USER_DATASET_VERSION_MIN_ID if current_max_id < USER_DATASET_VERSION_MIN_ID \
                else current_max_id + 1
            new_version.save()
            # need to remove this one, otherwise it will be duplicated
            DatasetVersion.objects.get(id=new_version_id).delete()
        return new_version
    else:
        raise Exception(version_serializer.errors)


def create_dataset_entry(dataset_name, dataset_pretty_name, version, user, is_scattered_data=False):
    current_max_id = Dataset.objects.all().last().id if Dataset.objects.all(
    ) else 0
    dataset_data = {
        'short_name': dataset_name,
        'pretty_name': dataset_pretty_name,
        'help_text': f'Dataset {dataset_pretty_name} provided by user {user}.',
        'storage_path': '',
        'detailed_description': 'Data provided by a user',
        'source_reference': 'Data provided by a user',
        'citation': 'Data provided by a user',
        'resolution': None,
        'user': user.pk,
        'versions': [version.pk],
        'is_scattered_data': is_scattered_data,
    }

    dataset_serializer = DatasetSerializer(data=dataset_data)
    if dataset_serializer.is_valid():
        new_dataset = dataset_serializer.save()
        new_dataset_id = new_dataset.id
        # need to leave some id spots for our datasets, to avoid overriding users' entries
        if new_dataset_id < USER_DATASET_MIN_ID:
            new_dataset.id = USER_DATASET_MIN_ID if current_max_id < USER_DATASET_MIN_ID else current_max_id + 1
            new_dataset.save()
            # need to remove this one, otherwise it will be duplicated
            Dataset.objects.get(id=new_dataset_id).delete()
        return new_dataset
    else:
        raise Exception(dataset_serializer.errors)


def update_file_entry(file_entry, dataset, version, variable, user,
                      all_variables):
    # file data
    file_data = {
        'file': file_entry.file,
        'owner': user.pk,
        'file_name': file_entry.file_name,
        'upload_date': file_entry.upload_date,
        'dataset': dataset.id,
        'version': version.id,
        'variable': variable.id if variable else None,
        'all_variables': all_variables,
    }

    file_data_serializer = UploadSerializer(data=file_data)

    if file_data_serializer.is_valid() and user == file_entry.owner:
        file_entry.dataset = dataset
        file_entry.version = version
        file_entry.variable = variable
        file_entry.all_variables = file_data['all_variables']
        file_entry.save()
        response = {'data': file_data_serializer.data, 'status': 200}
    else:
        file_entry.delete()
        response = {'data': file_data_serializer.errors, 'status': 500}
    return response


def preprocess_file(file_serializer, file_raw_path, user_path):
    connections.close_all()
    p = Process(target=user_data_preprocessing,
                kwargs={
                    "file_uuid": file_serializer.data['id'],
                    "file_path":
                    file_raw_path + file_serializer.data['file_name'],
                    "file_raw_path": file_raw_path,
                    "user_path": user_path
                })
    p.start()
    return


# API VIEWS


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_metadata(request, file_uuid):
    file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)
    field_name = request.data[USER_DATA_FIELD_NAME]
    field_value = request.data[USER_DATA_FIELD_VALUE]
    current_variable = file_entry.variable
    current_dataset = file_entry.dataset
    current_version = file_entry.version

    # for variable and dimensions we store a list of potential names and a value from this list can be chosen
    if field_name not in [
            USER_DATA_DATASET_FIELD_NAME, USER_DATA_VERSION_FIELD_NAME
    ]:
        new_item = next(item for item in file_entry.all_variables
                        if item["name"] == field_value)

        current_variable.pretty_name = new_item['long_name']
        current_variable.short_name = new_item['name']
        # can't simply use .get, because the key may exist but the unit assigned can be None
        current_variable.unit = new_item.get('units') if new_item.get(
            'units') else 'n.a.'
        current_variable.help_text = f'Variable {new_item["name"]} of dataset ' \
                                     f'{current_dataset.pretty_name} provided by user {request.user}.'
        current_variable.save()

    elif field_name == USER_DATA_DATASET_FIELD_NAME:
        current_dataset.pretty_name = field_value
        current_dataset.save()
    elif field_name == USER_DATA_VERSION_FIELD_NAME:
        current_version.pretty_name = field_value
        current_version.save()

    return JsonResponse({'variable_id': current_variable.id}, status=200)


class UploadedFileError(BaseException):

    def __init__(self, message):
        super(BaseException, self).__init__()
        self.message = message


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([FileUploadParser])
def upload_user_data(request, filename):
    user = request.user.username
    user_data_dir = getattr(settings, 'USER_DATA_DIR', '/tmp/user_data_dir/')
    user_path = Path(user_data_dir) / user / 'log'
    user_path.mkdir(parents=True, exist_ok=True)

    file = request.FILES['file']

    #  get metadata
    metadata = json.loads(request.META.get('HTTP_FILEMETADATA'))

    serializer = UserFileMetadataSerializer(data=metadata)

    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=500, safe=False)

    dataset_name = metadata[USER_DATA_DATASET_FIELD_NAME]
    dataset_pretty_name = metadata[
        USER_DATA_DATASET_FIELD_PRETTY_NAME] if metadata[
            USER_DATA_DATASET_FIELD_PRETTY_NAME] else dataset_name
    version_name = metadata[USER_DATA_VERSION_FIELD_NAME]
    version_pretty_name = metadata[
        USER_DATA_VERSION_FIELD_PRETTY_NAME] if metadata[
            USER_DATA_VERSION_FIELD_PRETTY_NAME] else version_name

    # needs file operation bc zip could also contain nc file (i.e.: internal case not relevant for users)
    is_scattered = has_csv_in_zip(file)

    # creating version entry

    new_variable = create_variable_entry('none', 'none', dataset_pretty_name,
                                         request.user, 'n.a.')
    new_version = create_version_entry(version_name, version_pretty_name,
                                       dataset_pretty_name, request.user,
                                       new_variable)
    new_dataset = create_dataset_entry(dataset_name, dataset_pretty_name,
                                       new_version, request.user, is_scattered_data=is_scattered)

    file_data = {
        'file': file,
        'file_name': filename,
        'owner': request.user.pk,
        'dataset': new_dataset.pk,
        'version': new_version.pk,
        'variable': new_variable.pk,
        'upload_date': timezone.now(),
        'user_groups': []
    }

    file_serializer = UploadFileSerializer(data=file_data)
    if file_serializer.is_valid():
        # saving file
        try:
            file_serializer.save()
        except Exception as e:
            new_dataset.delete()
            new_variable.delete()
            new_version.delete()
            return JsonResponse(
                {
                    'error':
                    'We could not save your file. Please try again later or contact our team'
                    ' to get help.'
                },
                status=500,
                safe=False)

        success, msg, status = run_upload_format_check(
            file=file,
            filename=filename,
            file_uuid=file_serializer.data['id'],
            user_path=user_path)
        if not success:
            # angular error flow handles both str or dict (userFileUpload)
            return JsonResponse(msg, status=status, safe=False)

        # need to get the path and assign it to the dataset as well as pass it to preprocessing function, so I don't
        # have to open the db connection before file preprocessing.
        file_raw_path = file_serializer.data['get_raw_file_path']
        preprocess_file(file_serializer, file_raw_path, user_path)

        return JsonResponse(file_serializer.data, status=201, safe=False)
    else:
        print(file_serializer.errors)
        return JsonResponse(file_serializer.errors, status=500, safe=False)


# SERIALIZERS
class UploadSerializer(ModelSerializer):

    class Meta:
        model = UserDatasetFile
        fields = get_fields_as_list(UserDatasetFile)


class UploadFileSerializer(ModelSerializer):

    class Meta:
        model = UserDatasetFile
        fields = get_fields_as_list(UserDatasetFile)

    requires_context = True

    def create(self, validated_data):
        instance = super().create(validated_data)
        with transaction.atomic():
            instance.save()
        return instance


class DatasetSerializer(ModelSerializer):

    class Meta:
        model = Dataset
        fields = [
            'id', 'short_name', 'pretty_name', 'help_text', 'storage_path',
            'detailed_description', 'source_reference', 'citation', 'versions',
            'user', 'is_scattered_data'
        ]


class DataManagementGroupSerializer(ModelSerializer):

    class Meta:
        model = DataManagementGroup
        fields = get_fields_as_list(model)


class DatasetVersionSerializer(ModelSerializer):

    class Meta:
        model = DatasetVersion
        fields = '__all__'


class DatasetVariableSerializer(ModelSerializer):

    class Meta:
        model = DataVariable
        fields = '__all__'


class UserFileMetadataSerializer(Serializer):
    # with this serializer I'm checking if the metadata is properly introduced, but the metadata doesn't refer to any
    # particular model, therefore it's not a model serializer
    dataset_name = serializers.CharField(max_length=30, required=True)
    dataset_pretty_name = serializers.CharField(max_length=30,
                                                required=False,
                                                allow_blank=True,
                                                allow_null=True)
    version_name = serializers.CharField(max_length=30, required=True)
    version_pretty_name = serializers.CharField(max_length=30,
                                                required=False,
                                                allow_blank=True,
                                                allow_null=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
