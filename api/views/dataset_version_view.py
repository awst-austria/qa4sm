from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.serializers import ModelSerializer
from rest_framework.authentication import TokenAuthentication

from validator.models import DatasetVersion, Dataset


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
            else:
                return JsonResponse(
                    {'message': 'Version could not be updated. Please check the data you are trying to pass.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e:
            return JsonResponse(
                {'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({'message': 'Updated'}, status=status.HTTP_200_OK, safe=False)


def field_validator(data, model_serializer):
    model_fields = set(model_serializer().fields)
    data_keys = set(data.keys())
    if not data_keys.issubset(model_fields):
        raise KeyError('Submitted data contains a wrong key.')
    return data


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
