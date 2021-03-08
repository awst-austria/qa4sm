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

    serializer = ResultsSerializer(paginated_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_results(request):
    page = request.GET.get('page', 1)

    # toDO: val_runs should be filtered by user
    val_runs = ValidationRun.objects.all()

    paginator = Paginator(val_runs, 10)
    try:
        paginated_runs = paginator.page(page)
    except PageNotAnInteger:
        paginated_runs = paginator.page(1)
    except EmptyPage:
        paginated_runs = paginator.page(paginator.num_pages)

    serializer = ResultsSerializer(paginated_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


class ResultsSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(ValidationRun)
