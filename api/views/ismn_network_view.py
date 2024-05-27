import json

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from validator.models import ISMNNetworks


@api_view(['GET'])
@permission_classes([AllowAny])
def get_ismn_networks(request):
    dataset_id = None

    if 'id' in request.query_params:
        dataset_id = request.query_params['id']

    networks = None

    if dataset_id is not None:
        networks = ISMNNetworks.objects.filter(versions__id=dataset_id)
    else:
        networks = ISMNNetworks.objects.all()

    network_list = []
    for net in networks:
        network = {'name': net.name, 'continent': net.continent, 'stations': net.number_of_stations, 'country': net.country}
        network_list.append(network)

    return JsonResponse(network_list, safe=False)
