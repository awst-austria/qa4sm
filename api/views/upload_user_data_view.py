from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
import io

from validator.models import UserDatasetFile, DatasetVersion, DataVariable, Dataset

import netCDF4 as nc

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_list_of_user_data_files(request):
    list_of_files = UserDatasetFile.objects.filter(owner=request.user)
    serializer = UploadSerializer(list_of_files, many=True)
    return JsonResponse(serializer.data, status=200, safe=False)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_dataset(request, dataset_id):
    dataset_file = get_object_or_404(UserDatasetFile, pk=dataset_id)

    if dataset_file.owner != request.user:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    dataset = get_object_or_404(Dataset, id=dataset_file.dataset.id)
    version = get_object_or_404(DatasetVersion, id=dataset_file.version.id)
    variable = get_object_or_404(DataVariable, id=dataset_file.variable.id)

    dataset.variables.clear()
    dataset.versions.clear()
    dataset.filters.clear()

    dataset.delete()
    version.delete()
    variable.delete()

    dataset_file.delete()

    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
def post_user_file_metadata(request, file_uuid):
    serializer = UserFileMetadataSerializer(data=request.data)
    file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)

    if serializer.is_valid():
        dataset_name = request.data['dataset_name']
        dataset_pretty_name = request.data['dataset_pretty_name']
        version_name = request.data['version_name']
        version_pretty_name = request.data['version_pretty_name']
        variable_name = request.data['variable_name']
        dimension_name = request.data['dimension_name']

        # creating version entry
        new_version_data = {
            "short_name": version_name,
            "pretty_name": version_pretty_name if version_pretty_name else version_name,
            "help_text": f'Version {version_pretty_name} of dataset {dataset_pretty_name} provided by user {request.user}.',
            "time_range_start": None,
            "time_range_end": None,
            "geographical_range": None,
        }
        new_version = DatasetVersion(**new_version_data)
        new_version.save()

        # creating variable entry
        new_variable_data = {
            'short_name': variable_name,
            'pretty_name': variable_name,
            'help_text': f'Variable {variable_name} of dataset {dataset_pretty_name} provided by  user {request.user}.',
            'min_value': None,
            'max_value': None
        }
        new_variable = DataVariable(**new_variable_data)
        new_variable.save()

        # creating dataset entry
        new_dataset_data = {
            'short_name': dataset_name,
            'pretty_name': dataset_pretty_name if dataset_pretty_name else dataset_name,
            'help_text': f'Dataset {dataset_pretty_name} provided by user {request.user}.',
            'storage_path': file_entry.file.path,
            'detailed_description': 'Data provided by a user',
            'source_reference': 'Data provided by a user',
            'citation': 'Data provided by a user',
            'resolution': None,
            'user': request.user
        }
        new_dataset = Dataset(**new_dataset_data)
        new_dataset.save()
        new_dataset.versions.set([new_version.id])
        new_dataset.filters.set([])
        new_dataset.variables.set([new_variable.id])

        # file data
        file_data = {
            'file': file_entry.file,
            'owner': request.user.pk,
            'file_name': file_entry.file_name,
            'dataset': new_dataset.id,
            'version': new_version.id,
            'variable': new_variable.id
        }

        file_data_serializer = UploadSerializer(data=file_data)
        if file_data_serializer.is_valid() and request.user == file_entry.owner:
            try:
                file_entry.dataset = new_dataset
                file_entry.version = new_version
                file_entry.variable = new_variable
                file_entry.save()

            except:
                file_entry.delete()
                return JsonResponse({'message': 'Metadata could not be assigned to the file'}, status=500, safe=False)

            return JsonResponse(file_data_serializer.data, status=200, safe=False)
        else:
            return JsonResponse(file_data_serializer.errors, status=500, safe=False)
    else:
        # file entry has to be deleted if metadata is not stored
        file_entry.delete()
        return JsonResponse(serializer.errors, status=500, safe=False)


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([FileUploadParser])
def upload_user_data(request, filename):
    file = request.FILES['file']
    # file_entry = get_object_or_404(UserDatasetFile, id=file_uuid)

    file_data = {
        'file': file,
        'file_name': filename,
        'owner': request.user.pk,
        'dataset': None,
        'version': None,
        'variable': None
    }

    file_serializer = UploadSerializer(data=file_data)

    if file_serializer.is_valid():
        file_serializer.save()
        response = file_serializer.data
    else:
        print(file_serializer.errors)
        response = file_serializer.errors

    return JsonResponse(response, status=200, safe=False)


# @api_view(['POST', 'PUT'])
# @permission_classes([IsAuthenticated])
# @parser_classes([FileUploadParser])
# def validate_user_data(request, filename,  file_uuid):
#     # serializer_class = UploadSerializer
#     file = request.data['file']
#     f = file.file
#     f.seek(0)
#     # f.seek(0)
#
#     ds = nc.Dataset(f.getvalue())
#     print(ds)
#
#     # print(dir(file), type(file), type(f))
#     # print(f.getvalue())
#     response = {'message': 'Monika'}
#     return JsonResponse(response, status=200, safe=False)

# def test_user_data(request, dataset_id):
#     import netCDF4 as nc
#     from zipfile import ZipFile
#
#     data_file = get_object_or_404(UserDatasetFile, id=dataset_id)
#     file_path = data_file.file.path
#     raw_path = file_path.rstrip(data_file.file_name)
#     if '.zip' in data_file.file_name:
#
#         with ZipFile(file_path, 'r') as zipObj:
#             zipObj.extractall(raw_path)
#         nc_file_name = data_file.file_name.rstrip('.zip') + '.nc'
#         # ds = nc.Dataset(raw_path + nc_file_name)
#         # print(ds)
#
#         of = open(raw_path + nc_file_name, "r")
#         print(of.read())
#
#     elif '.nc' in data_file.file_name:
#         # zip_file = data_file.file_name.rstrip('.nc') + '.zip'
#         # zipObj = ZipFile(raw_path + zip_file, 'w')
#         # zipObj.write(file_path)
#         # zipObj.close()
#         # with ZipFile(file_path, 'r') as zipObj:
#         #     zipObj.extractall(raw_path)
#         #
#         print('Monika')
#         ds = nc.Dataset(file_path)
#         print(ds)
#         # of = open(file_path, "r")
#         # print(of.read())
#
#     return JsonResponse({'message': 'ok'}, status=200)


class UploadSerializer(ModelSerializer):
    class Meta:
        model = UserDatasetFile
        fields = '__all__'


class UserFileMetadataSerializer(Serializer):
    # with this serializer I'm checking if the metadata is properly introduced, but the metadata doesn't refer to any
    # particular model, therefore it's not a model serializer
    dataset_name = serializers.CharField(max_length=30, required=True)
    dataset_pretty_name = serializers.CharField(max_length=30, required=False)
    version_name = serializers.CharField(max_length=30, required=True)
    version_pretty_name = serializers.CharField(max_length=30, required=False)
    variable_name = serializers.CharField(max_length=30, required=True)
    dimension_name = serializers.CharField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


# class UserFileSerializer(Serializer):
#     file = serializers.FileField(allow_null=True)
#     file_name = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
#
#     def create(self, validated_data):
#         pass
#
#     def update(self, instance, validated_data):
#         pass
