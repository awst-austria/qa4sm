import logging
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import Serializer

from validator.models import UptimeAgent, UptimePing
from validator.uptime import generate_daily_report, generate_monthly_report

__logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def uptime_ping(request):
    request_serializer = UptimePingSerializer(data=request.data)
    if request_serializer.is_valid() is False:
        __logger.warning("Invalid uptime ping. " + request.data)
        return HttpResponse("Invalid request", status=400)
    agent_key = request_serializer.validated_data.get('agent_key')
    try:
        uptime_agent = UptimeAgent.objects.get(agent_key=agent_key)
        ping = UptimePing()
        ping.agent_key = uptime_agent.agent_key
        ping.save()
    except Exception as e:
        __logger.warning(e)
        return HttpResponse("Invalid request", status=400)

    return HttpResponse("OK", status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_uptime(request):
    day = datetime(year=2021, month=4, day=5)
    generate_daily_report(day)
    generate_monthly_report(year=2021, month=4)
    return JsonResponse('Nyaloka', status=200, safe=False)


class UptimePingSerializer(Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    agent_key = serializers.CharField(max_length=200, required=True)
