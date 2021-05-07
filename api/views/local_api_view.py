from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from django.http import JsonResponse
from django_countries import countries


@api_view(['GET'])
@permission_classes([AllowAny])
def get_list_of_countries(request):
    country_dict = countries.countries
    response = [{'abbreviation': key, 'name': country_dict[key]} for key in country_dict]
    return JsonResponse(response, safe=False)