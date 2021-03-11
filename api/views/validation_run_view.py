from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from api.views.auxiliary_functions import get_fields_as_list
from validator.models import ValidationRun


@api_view(['GET'])
@permission_classes([AllowAny])
def published_results_paginated(request):
    limit = int(request.query_params.get('limit', 10))
    offset = int(request.query_params.get('offset', 0))

    val_runs = ValidationRun.objects.exclude(doi='').order_by('-start_time')

    serializer = ResultsSerializer(val_runs[offset:(offset+limit)], many=True)
    return JsonResponse(({'validations': serializer.data, 'length': len(val_runs)}), status=status.HTTP_200_OK, safe=False)



@api_view(['GET'])
@permission_classes([AllowAny])
def published_results(request):
    limit = int(request.query_params.get('limit', None))
    offset = int(request.query_params.get('offset', None))

    val_runs = ValidationRun.objects.exclude(doi='').order_by('-start_time')

    serializer = ResultsSerializer(val_runs[offset:(offset+limit)], many=True)
    response = {'validations': serializer.data, 'length': len(val_runs)}
    return JsonResponse(response, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_results(request):
    current_user = request.user
    limit = int(request.query_params.get('limit', None))
    offset = int(request.query_params.get('offset', None))

    val_runs = ValidationRun.objects.filter(user=current_user).order_by('-start_time')

    serializer = ResultsSerializer(val_runs[offset:(offset+limit)], many=True)
    response = {'validations': serializer.data, 'length': len(val_runs)}

    return JsonResponse(response, status=status.HTTP_200_OK, safe=False)


class ResultsSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(ValidationRun)
