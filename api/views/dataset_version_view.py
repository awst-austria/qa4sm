import json
import os
import logging

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.authentication import TokenAuthentication

from validator.models import DatasetVersion, Dataset
from api.views.auxiliary_functions import push_changes_to_github
__logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_version(request):
    versions = DatasetVersion.objects.all().order_by('-id')
    serializer = DatasetVersionSerializer(versions, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_version_by_id(request, **kwargs):
    version = get_object_or_404(DatasetVersion, id=kwargs['version_id'])
    serializer = DatasetVersionSerializer(version)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_version_by_dataset(request, **kwargs):
    versions = get_object_or_404(Dataset, id=kwargs['dataset_id']).versions.order_by('id')
    serializer = DatasetVersionSerializer(versions, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([TokenAuthentication])
def update_dataset_version(request):
    for element in request.data:
        version = get_object_or_404(DatasetVersion, id=element.get('id'))
        try:
            validated_data = field_validator(element, DatasetVersionSerializer)
            version_serializer = DatasetVersionSerializer(version, data=validated_data, partial=True)
            if version_serializer.is_valid():
                version_serializer.save()
                update_fixture_entry(version)
            else:
                return JsonResponse(
                    {'message': 'Version could not be updated. Please check the data you are trying to pass.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e:
            return JsonResponse(
                {'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({'message': 'Updated'}, status=status.HTTP_200_OK, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([TokenAuthentication])
def update_fixture_in_github(request):
    """
    Updates the version fixture on GitHub by committing the changes to the repository.
    The fixture is located at 'validator/fixtures/versions.json' and the changes are
    pushed to the 'master' branch.

    :param request: The HTTP request object.
    :return: A JSON response indicating success or failure.
    """
    __logger.debug(f'I triggered the api call')
    branch_name = 'main' #'main' - nominally will be main, let's test it for now
    file_name = os.path.join('validator', 'fixtures', 'versions.json')
    commit_message = 'Version fixture updated'

    try:
        push_changes_to_github(file_name, commit_message, branch_name)
        return Response({'message': 'All good'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def field_validator(data, model_serializer):
    model_fields = set(model_serializer().fields)
    data_keys = set(data.keys())
    if not data_keys.issubset(model_fields):
        raise KeyError('Submitted data contains a wrong key.')
    return data


def update_fixture_entry(version):
    # Path to the fixture
    fixture_path = os.path.join(settings.BASE_DIR, 'validator', 'fixtures', 'versions.json')

    # Read the existing fixture file
    with open(fixture_path, 'r', encoding='utf-8') as f:
        fixture_data = json.load(f)

    # Find the entry matching the updated version
    for entry in fixture_data:
        print(entry)
        if entry["model"] == "validator.datasetversion" and entry["pk"] == version.pk:
            # Update fields with the current DB data
            entry_fields = entry["fields"]
            for key in entry_fields.keys():
                try:
                    # Handle many-to-many relationships
                    if hasattr(version, key) and isinstance(getattr(version, key), (list, set, tuple)):
                        entry_fields[key] = list(getattr(version, key).values_list('id', flat=True))
                    elif hasattr(version, key) and hasattr(getattr(version, key), 'all'):  # For ManyRelatedManager
                        entry_fields[key] = list(getattr(version, key).all().values_list('id', flat=True))
                    # Handle foreign key relationships
                    elif hasattr(version, key) and hasattr(getattr(version, key), 'pk'):
                        entry_fields[key] = getattr(version, key).pk
                    else:
                        # Default: Use the attribute directly
                        entry_fields[key] = getattr(version, key)
                except AttributeError:
                    # Skip keys that don't map directly to the version object
                    pass
            break  # Exit the loop once the relevant entry is updated

    # Write the updated data back to the fixture file
    with open(fixture_path, 'w', encoding='utf-8') as f:
        json.dump(fixture_data, f, cls=DjangoJSONEncoder, indent=4)


class DatasetVersionSerializer(ModelSerializer):
    class Meta:
        model = DatasetVersion
        fields = ['id',
                  'short_name',
                  'pretty_name',
                  'help_text',
                  'filters',  # new
                  'time_range_start',
                  'time_range_end',
                  'geographical_range'
                  ]
