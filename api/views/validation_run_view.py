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
def published_results(request):
    page = request.GET.get('page', 1)

    val_runs = ValidationRun.objects.exclude(doi='')

    paginator = Paginator(val_runs, 10)
    try:
        paginated_runs = paginator.page(page)
    except PageNotAnInteger:
        paginated_runs = paginator.page(1)
    except EmptyPage:
        paginated_runs = paginator.page(paginator.num_pages)

    serializer = ValidationRunSerializer(paginated_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_results(request):
    page = request.GET.get('page', 1)

    val_runs = ValidationRun.objects.filter(user=request.user)

    paginator = Paginator(val_runs, 10)
    try:
        paginated_runs = paginator.page(page)
    except PageNotAnInteger:
        paginated_runs = paginator.page(1)
    except EmptyPage:
        paginated_runs = paginator.page(paginator.num_pages)

    serializer = ValidationRunSerializer(paginated_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validation_runs(request, **kwargs):
    val_runs = ValidationRun.objects.all()
    serializer = ValidationRunSerializer(val_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validation_run_by_id(request, **kwargs):
    val_run = ValidationRun.objects.get(pk=kwargs['id'])
    if val_run is None:
        return JsonResponse(None, status=status.HTTP_404_NOT_FOUND, safe=False)

    serializer = ValidationRunSerializer(val_run)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


class ValidationRunSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(ValidationRun)
