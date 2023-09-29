from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import IsAuthenticated

from api.views.upload_user_data_view import DataManagementGroupSerializer, UploadSerializer
from validator.models import UserDatasetFile, DataManagementGroup

import logging

__logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_data_management_groups(request):
    groups_ids = request.GET.getlist('id')
    groups = DataManagementGroup.objects.all()
    if len(groups_ids):
        groups = groups.filter(id__in=groups_ids)
    serializer = DataManagementGroupSerializer(groups, many=True)
    try:
        return JsonResponse(serializer.data, status=200, safe=False)
    except:
        return JsonResponse({'message': 'Something went wrong'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_data_management_groups(request):
    # here I'll create a new data management group
    pass
    # groups_ids = request.GET.getlist('id')
    # groups = DataManagementGroup.objects.all()
    # if len(groups_ids):
    #     groups = groups.filter(id__in=groups_ids)
    # serializer = DataManagementGroupSerializer(groups, many=True)
    #
    # try:
    #     return JsonResponse(serializer.data, status=200, safe=False)
    # except:
    #     return JsonResponse({'message': 'Something went wrong'}, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def manage_data_in_group(request):
    group_id = request.data.get('group_id')
    data_id = request.data.get('data_id')
    action = request.data.get('action')

    group = get_object_or_404(DataManagementGroup, pk=group_id)
    user_dataset = get_object_or_404(UserDatasetFile, pk=data_id)

    try:
        group.custom_datasets.add(user_dataset) if action == 'add' else group.custom_datasets.remove(user_dataset)
        return JsonResponse({'message': 'Ok'}, status=200)
    except:
        return JsonResponse({'message': 'Something went wrong'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_list_of_user_data_files(request):
    list_of_files = UserDatasetFile.objects.filter(owner=request.user).order_by('-upload_date')
    serializer = UploadSerializer(list_of_files, many=True)
    try:
        return JsonResponse(serializer.data, status=200, safe=False)
    except:
        return JsonResponse({'message': 'We could not return the list of your datafiles'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data_file_by_id(request, file_uuid):
    file_entry = get_object_or_404(UserDatasetFile, pk=file_uuid)

    if file_entry.owner != request.user:
        return JsonResponse({'detail': 'Not found.'}, status=404)

    serializer = UploadSerializer(file_entry, many=False)
    return JsonResponse(serializer.data, status=200, safe=False)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_dataset_and_file(request, file_uuid):
    file_entry = get_object_or_404(UserDatasetFile, pk=file_uuid)
    if file_entry.owner != request.user:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    file_entry.delete()

    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_dataset_file_only(request, file_uuid):
    file_entry = get_object_or_404(UserDatasetFile, pk=file_uuid)
    if file_entry.owner != request.user:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    file_entry.delete_dataset_file()
    return HttpResponse(status=status.HTTP_200_OK)
