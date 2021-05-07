from django.http import HttpResponse, JsonResponse
from django_countries.serializer_fields import CountryField
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.fields import DateTimeField, CharField
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from django_countries import countries

from validator.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users(request):
    if request.user.is_superuser:
        print('super')

    user = User.objects.all()
    serializer = UserSerializer(user, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signup_post(request):
    print(request)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_list_od_countries(request):
    country_dict = countries.countries
    response = [{'abbreviation': key, 'name': country_dict[key]} for key in country_dict]
    return JsonResponse(response, safe=False)


class UserSerializer(ModelSerializer):
    last_login = DateTimeField(read_only=True)
    date_joined = DateTimeField(read_only=True)
    password = CharField(write_only=True)
    country = CountryField()

    class Meta:
        model = User
        fields = ['username',
                  'password',
                  'email',
                  'first_name',
                  'last_name',
                  'organisation',
                  'last_login',
                  'date_joined',
                  'country',
                  'orcid',
                  'id',
                  'copied_runs']
