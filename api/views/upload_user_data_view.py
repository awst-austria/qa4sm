from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from django.utils import timezone

from api.views.auxiliary_functions import get_fields_as_list, clean_redundant_datasets
from validator.models import UserDatasetFile, DatasetVersion, DataVariable, Dataset
from api.variable_and_field_names import *
import logging
from qa4sm_preprocessing.utils import *
from validator.validation.globals import USER_DATASET_MIN_ID, USER_DATASET_VERSION_MIN_ID, USER_DATASET_VARIABLE_MIN_ID

__logger = logging.getLogger(__name__)


def create_variable_entry(variable_name, variable_pretty_name, dataset_name, user, variable_unit=None, max_value=None,
                          min_value=None):
    current_max_id = DataVariable.objects.all().last().id if DataVariable.objects.all().last() else 0
    new_variable_data = {
        'short_name': variable_name,
        'pretty_name': variable_pretty_name,
        'help_text': f'Variable {variable_name} of dataset {dataset_name} provided by  user {user}.',
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


def create_version_entry(version_name, version_pretty_name, dataset_pretty_name, user):
    current_max_id = DatasetVersion.objects.all().last().id if DatasetVersion.objects.all().last() else 0
    new_version_data = {
        "short_name": version_name,
        "pretty_name": version_pretty_name,
        "help_text": f'Version {version_pretty_name} of dataset {dataset_pretty_name} provided by user {user}.',
        "time_range_start": None,
        "time_range_end": None,
        "geographical_range": None,
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


def create_dataset_entry(dataset_name, dataset_pretty_name, version, variable, user, file_entry):
    # TODO: update variables
    current_max_id = Dataset.objects.all().last().id if Dataset.objects.all() else 0
    dataset_data = {
        'short_name': dataset_name,
        'pretty_name': dataset_pretty_name,
        'help_text': f'Dataset {dataset_pretty_name} provided by user {user}.',
        'storage_path': file_entry.get_raw_file_path,
        'detailed_description': 'Data provided by a user',
        'source_reference': 'Data provided by a user',
        'citation': 'Data provided by a user',
        'resolution': None,
        'user': user.pk,
        'versions': [version.pk],
        'variables': [variable.pk],
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


def update_file_entry(file_entry, dataset, version, variable, user, all_variables):
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


def get_sm_variable_names(variables):
    key_sm_words = ['water', 'soil', 'moisture', 'soil_moisture', 'sm', 'ssm', 'water_content', 'soil', 'moisture',
                    'swi', 'swvl1', 'soilmoi']
    key_error_words = ['error', 'bias', 'uncertainty']
    candidates = [variable for variable in variables if any([word in variable.lower() for word in key_sm_words])
                  and not any([word in variable.lower() for word in key_error_words])]

    sm_variables = [{
        'name': var,
        'long_name': variables[var].get("long_name", var),
        'units': variables[var].get("units") if variables[var].get("units") else 'n.a.'
    } for var in candidates]

    if len(sm_variables) > 0:
        return sm_variables[0]
    else:
        return {'name': '--none--',
                'long_name': '--none--',
                'units': 'n.a.'}


def get_variables_from_the_reader(reader):
    variables = reader.variable_description()
    variables_dict_list = [
        {'name': variable,
         'long_name': variables[variable].get("long_name", variables[variable].get("standard_name", variable)),
         'units': variables[variable].get("units") if variables[variable].get("units") else 'n.a.'
         }
        for variable in variables
    ]

    return variables_dict_list


# API VIEWS


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_list_of_user_data_files(request):
    list_of_files = UserDatasetFile.objects.filter(owner=request.user).order_by('-upload_date')
    user_datasets_without_file = Dataset.objects.filter(user=request.user).filter(user_dataset__isnull=True)
    if len(user_datasets_without_file) != 0:
        try:
            clean_redundant_datasets(user_datasets_without_file)
        except:
            print(f'Could not remove datasets, versions and variables for user {request.user}')

    serializer = UploadSerializer(list_of_files, many=True)
    try:
        return JsonResponse(serializer.data, status=200, safe=False)
    except:
        # this exception is to catch a situation when the file doesn't exist, or in our case is rather about problems
        # with proper path bound to a docker container
        return JsonResponse({'message': 'We could not return the list of your datafiles'}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_dataset_and_file(request, file_uuid):
    file_entry = get_object_or_404(UserDatasetFile, pk=file_uuid)
    if file_entry.owner != request.user:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    file_entry.delete()

    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_metadata(request, file_uuid):
    # TODO: update this one with the new approach to the variable issue
    file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)
    field_name = request.data[USER_DATA_FIELD_NAME]
    field_value = request.data[USER_DATA_FIELD_VALUE]
    current_variable = file_entry.variable
    current_dataset = file_entry.dataset
    current_version = file_entry.version

    # for variable and dimensions we store a list of potential names and a value from this list can be chosen
    if field_name not in [USER_DATA_DATASET_FIELD_NAME, USER_DATA_VERSION_FIELD_NAME]:
        new_item = next(item for item in file_entry.all_variables if item["name"] == field_value)

        current_variable.pretty_name = new_item['long_name']
        current_variable.short_name = new_item['name']
        # can't simply use .get, because the key may exist but the unit assigned can be None
        current_variable.unit = new_item.get('units') if new_item.get('units') else 'n.a.'
        current_variable.help_text = f'Variable {new_item["name"]} of dataset ' \
                                     f'{current_dataset.pretty_name} provided by user {request.user}.'
        current_variable.save()

    elif field_name == USER_DATA_DATASET_FIELD_NAME:
        current_dataset.pretty_name = field_value
        current_dataset.save()
    elif field_name == USER_DATA_VERSION_FIELD_NAME:
        current_version.pretty_name = field_value
        current_version.save()

    # todo Update the response
    return JsonResponse({'variable_id': current_variable.id}, status=200)


class UploadedFileError(BaseException):
    def __init__(self, message):
        super(BaseException, self).__init__()
        self.message = message


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
def post_user_file_metadata_and_preprocess_file(request, file_uuid):
    serializer = UserFileMetadataSerializer(data=request.data)
    file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)
    file_entry.metadata_submitted = True
    file_entry.save()

    if serializer.is_valid():
        # first the file will be preprocessed
        try:
            gridded_reader = preprocess_user_data(file_entry.file.path, file_entry.get_raw_file_path + '/timeseries')
        except Exception as e:
            print(e, type(e))
            file_entry.delete()
            return JsonResponse({'error': 'Provided file does not fulfill requirements.'}, status=500, safe=False)

        sm_variable = get_sm_variable_names(gridded_reader.variable_description())
        all_variables = get_variables_from_the_reader(gridded_reader)

        dataset_name = request.data[USER_DATA_DATASET_FIELD_NAME]
        dataset_pretty_name = request.data[USER_DATA_DATASET_FIELD_PRETTY_NAME] if request.data[
            USER_DATA_DATASET_FIELD_PRETTY_NAME] else dataset_name
        version_name = request.data[USER_DATA_VERSION_FIELD_NAME]
        version_pretty_name = request.data[USER_DATA_VERSION_FIELD_PRETTY_NAME] if request.data[
            USER_DATA_VERSION_FIELD_PRETTY_NAME] else version_name
        #
        # creating version entry
        new_version = create_version_entry(version_name, version_pretty_name, dataset_pretty_name, request.user)
        # creating variable entry

        new_variable = create_variable_entry(sm_variable['name'], sm_variable['long_name'], dataset_pretty_name,
                                             request.user, sm_variable['units'])
        # for sm_variable in sm_variables:
        #     new_variable = create_variable_entry(
        #             sm_variable['name'],
        #             sm_variable['long_name'],
        #             dataset_pretty_name,
        #             request.user)
        # creating dataset entry
        new_dataset = create_dataset_entry(dataset_name, dataset_pretty_name, new_version, new_variable, request.user,
                                           file_entry)
        # updating file entry
        file_data_updated = update_file_entry(file_entry, new_dataset, new_version, new_variable, request.user,
                                              all_variables)

        return JsonResponse(file_data_updated['data'], status=file_data_updated['status'], safe=False)

    else:
        print(serializer.errors)
        file_entry.delete()
        return JsonResponse(serializer.errors, status=500, safe=False)


def _verify_file_extension(file_name):
    return file_name.endswith('.nc4') or file_name.endswith('.nc') or file_name.endswith('.zip')


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([FileUploadParser])
def upload_user_data(request, filename):
    file = request.FILES['file']
    # I don't think it is possible not to meet this condition, but just in case
    if file.name != filename:
        return JsonResponse({'error': 'Wrong file name'}, status=500, safe=False)
    if not _verify_file_extension(filename):
        return JsonResponse({'error': 'Wrong file format'}, status=500, safe=False)
    if request.user.space_left and file.size > request.user.space_left:
        return JsonResponse({'error': 'File is too big'}, status=500, safe=False)

    file_data = {
        'file': file,
        'file_name': filename,
        'owner': request.user.pk,
        'dataset': None,
        'version': None,
        'variable': None,
        'upload_date': timezone.now()
    }

    file_serializer = UploadSerializer(data=file_data)
    if file_serializer.is_valid():
        file_serializer.save()
        return JsonResponse(file_serializer.data, status=200, safe=False)
    else:
        print(file_serializer.errors)
        return JsonResponse(file_serializer.errors, status=500, safe=False)


# SERIALIZERS
class UploadSerializer(ModelSerializer):
    class Meta:
        model = UserDatasetFile
        fields = get_fields_as_list(UserDatasetFile)


class DatasetSerializer(ModelSerializer):
    # this serializer do not verify filters field, as the field is required and for now we don't provide any
    class Meta:
        model = Dataset
        fields = ['id',
                  'short_name',
                  'pretty_name',
                  'help_text',
                  'storage_path',
                  'detailed_description',
                  'source_reference',
                  'citation',
                  'versions',
                  'variables',
                  'user'
                  ]


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
    dataset_pretty_name = serializers.CharField(max_length=30, required=False, allow_blank=True, allow_null=True)
    version_name = serializers.CharField(max_length=30, required=True)
    version_pretty_name = serializers.CharField(max_length=30, required=False, allow_blank=True, allow_null=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
