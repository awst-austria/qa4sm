import logging
from datetime import datetime

import pytz
from django.http import HttpResponse, JsonResponse
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import Serializer

from validator.models import UptimeAgent, UptimePing
from validator.uptime import generate_daily_report, generate_monthly_report, get_report

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
        ping.time = datetime.now(tz=pytz.UTC)
        ping.save()
    except Exception as e:
        __logger.warning(e)
        return HttpResponse("Invalid request", status=400)

    date_for_report = datetime.now(tz=pytz.UTC)
    generate_daily_report(date_for_report)
    generate_monthly_report(date_for_report.year, date_for_report.month)

    return HttpResponse("OK", status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_uptime(request):
    try:
        period_param = request.query_params['period']
        start_date_param = datetime.strptime(request.query_params['start-date'], '%Y-%m-%d')
        start_date = datetime(year=start_date_param.year, month=start_date_param.month, day=start_date_param.day,
                              tzinfo=pytz.UTC)

        uptime_report = get_report(period=period_param,
                                   date=start_date)
        uptime_percentage = 'None'
        downtime_minutes = 'None'
        if uptime_report is not None:
            uptime_percentage = uptime_report.uptime_percentage
            downtime_minutes = uptime_report.downtime_minutes

        resp = {'uptime_percentage': uptime_percentage, 'downtime_minutes': downtime_minutes}
        return JsonResponse(resp, status=200, safe=False)
    except Exception as e:
        __logger.warning(e)
        return HttpResponse("Invalid request", status=400)


class UptimePingSerializer(Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    agent_key = serializers.CharField(max_length=200, required=True)


DAILY = 'DAILY'
MONTHLY = 'MONTHLY'

PERIOD_OPTIONS = (
    (DAILY, 'daily'),
    (DAILY, 'monthly')
)


class UptimeRequestSerializer(Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    period = serializers.ChoiceField(choices=PERIOD_OPTIONS, required=True)
    start_date = serializers.DateTimeField(format="%Y-%m-%d", required=False, read_only=True)
