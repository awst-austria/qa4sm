from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from django.utils import timezone
from qa4sm_preprocessing.reading.cf import get_coord, get_time

from api.views.auxiliary_functions import get_fields_as_list
from validator.models import UserDatasetFile, DatasetVersion, DataVariable, Dataset
import xarray as xa


def create_variable_entry(variable_name, variable_pretty_name, dataset_name, user, max_value=None, min_value=None):
    new_variable_data = {
        'short_name': variable_name,
        'pretty_name': variable_pretty_name,
        'help_text': f'Variable {variable_name} of dataset {dataset_name} provided by  user {user}.',
        'min_value': max_value,
        'max_value': min_value
    }
    variable_serializer = DatasetVariableSerializer(data=new_variable_data)
    if variable_serializer.is_valid():
        new_variable = variable_serializer.save()
        return new_variable
    else:
        raise Exception(variable_serializer.errors)


def create_version_entry(version_name, version_pretty_name, dataset_pretty_name, user):
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
        return new_version
    else:
        raise Exception(version_serializer.errors)


def create_dataset_entry(dataset_name, dataset_pretty_name, version, variable, user, file_entry):
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
        return new_dataset
    else:
        raise Exception(dataset_serializer.errors)


def update_file_entry(file_entry, dataset, version, variable, user, metadata_from_file):
    # file data
    file_data = {
        'file': file_entry.file,
        'owner': user.pk,
        'file_name': file_entry.file_name,
        'upload_date': file_entry.upload_date,
        'dataset': dataset.id,
        'version': version.id,
        'variable': variable.id if variable else None,
        'lon_name': metadata_from_file['lon_name'],
        'lat_name': metadata_from_file['lat_name'],
        'time_name': metadata_from_file['time_name'],
        'all_variables': metadata_from_file['all_variables'],
    }

    file_data_serializer = UploadSerializer(data=file_data)

    if file_data_serializer.is_valid() and user == file_entry.owner:
        file_entry.dataset = dataset
        file_entry.version = version
        file_entry.variable = variable
        file_entry.lon_name = file_data['lon_name']
        file_entry.lat_name = file_data['lat_name']
        file_entry.time_name = file_data['time_name']
        file_entry.all_variables = file_data['all_variables']
        file_entry.save()
        response = {'data': file_data_serializer.data, 'status': 200}
    else:
        file_entry.delete()
        response = {'data': file_data_serializer.errors, 'status': 500}
    return response


def extract_coordinates_names(ncDataset):
    try:
        lon_name = get_coord(ncDataset, 'longitude', ['lon', 'longitude', 'y']).name
    except KeyError:
        lon_name = ''
    try:
        lat_name = get_coord(ncDataset, 'latitude', ['lat', 'latitude', 'x']).name
    except KeyError:
        lat_name = ''
    try:
        time_name = get_time(ncDataset).name
    except KeyError:
        time_name = ''

    return {
        'lon_name': lon_name,
        'lat_name': lat_name,
        'time_name': time_name,
    }


def extract_variable_names(ncDataset):
    variables = list(ncDataset.data_vars.keys())
    potential_variable_names = []
    key_sm_words = ['water', 'soil', 'moisture', 'soil_moisture', 'sm', 'ssm']
    key_error_words = ['error', 'bias', 'uncertainty']
    for variable in variables:
        if len(ncDataset.variables[variable].dims) == 3:
            try:
                variable_long_name = ncDataset.variables[variable].attrs['long_name']
            except KeyError:
                variable_long_name = ''
            try:
                variable_standard_name = ncDataset.variables[variable].attrs['standard_name']
            except KeyError:
                variable_standard_name = ''
            is_sm_word_in_variable_name = any([word in variable.lower() for word in key_sm_words])
            is_sm_word_in_long_name = any([word in variable_long_name.lower() for word in key_sm_words])
            is_sm_word_in_standard_name = any([word in variable_standard_name.lower() for word in key_sm_words])
            is_error_word_in_long_name = any([word in variable_long_name.lower() for word in key_error_words])
            if (is_sm_word_in_long_name or is_sm_word_in_standard_name or is_sm_word_in_variable_name) and \
                    not is_error_word_in_long_name:
                potential_variable_names.append({
                    'name': variable,
                    'standard_name': variable_standard_name if variable_standard_name else variable,
                    'long_name': variable_long_name if variable_long_name else (variable_standard_name if variable_standard_name else variable)
                })
    if len(potential_variable_names) == 0:
        potential_variable_names = [{'name': 'default_name',
                                     'standard_name': 'default_standard_name',
                                     'long_name': 'default_long_name'}]
    print(potential_variable_names)
    return potential_variable_names[0]


def retrieve_all_variables_from_netcdf(netCDF):
    file_variables = netCDF.variables
    variables_dict_list = [
        {'name': variable,
         'long_name':
             file_variables[variable].attrs['long_name']
             if 'long_name' in file_variables[variable].attrs.keys() else
             (file_variables[variable].attrs['standard_name'] if 'standard_name' in file_variables[
                 variable].attrs.keys() else variable)
         }
        for variable in file_variables
    ]
    return variables_dict_list


# API VIEWS

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_list_of_user_data_files(request):
    list_of_files = UserDatasetFile.objects.filter(owner=request.user).order_by('-upload_date')
    serializer = UploadSerializer(list_of_files, many=True)
    return JsonResponse(serializer.data, status=200, safe=False)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_dataset_and_file(request, dataset_id):
    file_entry = get_object_or_404(UserDatasetFile, pk=dataset_id)

    if file_entry.owner != request.user:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    dataset = get_object_or_404(Dataset, id=file_entry.dataset.id)
    version = get_object_or_404(DatasetVersion, id=file_entry.version.id)
    variable = get_object_or_404(DataVariable, id=file_entry.variable.id)

    dataset.variables.clear()
    dataset.versions.clear()
    dataset.filters.clear()

    dataset.delete()
    version.delete()
    variable.delete()

    file_entry.delete()

    return HttpResponse(status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_metadata(request, file_uuid):
    file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)
    field_name = request.data['field_name']
    field_value = request.data['field_value']
    current_variable = file_entry.variable
    current_dataset = file_entry.dataset
    current_version = file_entry.version

    if field_name not in ['dataset_name', 'version_name']:
        new_item = next(item for item in file_entry.all_variables if item["name"] == field_value)

    if field_name == 'variable_name':
        current_variable.short_name = new_item['name']
        current_variable.pretty_name = new_item['long_name']
        current_variable.help_text = f'Variable {new_item["name"]} of dataset ' \
                                     f'{current_dataset.pretty_name} provided by user {request.user}.'
        current_variable.save()
    elif field_name == 'dataset_name':
        current_dataset.pretty_name = field_value
        current_dataset.save()
    elif field_name == 'version_name':
        current_version.pretty_name = field_value
        current_version.save()
    else:
        setattr(file_entry, field_name, new_item['name'])
        file_entry.save()

    return JsonResponse({'variable_id': current_variable.id}, status=200)


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
def post_user_file_metadata(request, file_uuid):
    serializer = UserFileMetadataSerializer(data=request.data)
    file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)
    if serializer.is_valid():
        try:
            xarray_ds = xa.open_dataset(file_entry.file.path)
        except:
            file_entry.delete()
            return JsonResponse({'error': 'Wrong file format'}, status=500, safe=False)

        variable = extract_variable_names(xarray_ds)
        coordinates = extract_coordinates_names(xarray_ds)

        metadata_from_file = {
            'lat_name': coordinates['lat_name'],
            'lon_name': coordinates['lon_name'],
            'time_name': coordinates['time_name'],
            'variable': variable,
            'all_variables': retrieve_all_variables_from_netcdf(xarray_ds)
        }

        xarray_ds.close()

        dataset_name = request.data['dataset_name']
        dataset_pretty_name = request.data['dataset_pretty_name'] if request.data[
            'dataset_pretty_name'] else dataset_name
        version_name = request.data['version_name']
        version_pretty_name = request.data['version_pretty_name'] if request.data[
            'version_pretty_name'] else version_name

        # creating version entry
        new_version = create_version_entry(version_name, version_pretty_name, dataset_pretty_name, request.user)
        # creating variable entry

        new_variable = create_variable_entry(metadata_from_file['variable']['name'],
                                             metadata_from_file['variable']['long_name'],
                                             dataset_pretty_name,
                                             request.user)
        # creating dataset entry
        new_dataset = create_dataset_entry(dataset_name, dataset_pretty_name, new_version, new_variable, request.user,
                                           file_entry)
        # updating file entry
        file_data_updated = update_file_entry(file_entry, new_dataset, new_version, new_variable, request.user,
                                              metadata_from_file)

        return JsonResponse(file_data_updated['data'], status=file_data_updated['status'], safe=False)
    else:
        file_entry.delete()
        return JsonResponse(serializer.errors, status=500, safe=False)


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([FileUploadParser])
def upload_user_data(request, filename):
    file = request.FILES['file']

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
    dataset_pretty_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    version_name = serializers.CharField(max_length=30, required=True)
    version_pretty_name = serializers.CharField(max_length=30, required=False, allow_blank=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
