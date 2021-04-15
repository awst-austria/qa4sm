import logging
from calendar import monthrange

import pytz
from django.utils import timezone

from valentina.settings import UPTIME_PING_INTERVAL
from validator.models import UptimeReport, UptimePing, UptimeAgent
from datetime import datetime, timedelta

__logger = logging.getLogger(__name__)


def scheduled_task():
    print('Scheduled task. {0}'.format(datetime.now()))


def generate_daily_report(date, overwrite=False):
    """
    Takes the UptimePing table as input and generates a daily report for the date. Reports are stored
    in the UptimeReport table.
    Parameters
    ----------
    date: Subject day for the report
    overwrite: Overwrite existing reports

    Returns
    -------

    """
    if isinstance(date, datetime) is False:
        raise Exception('The date parameter should be date type')

    if date > datetime.now():
        raise Exception('Report cannot be generated for a future date')

    if date.date() == datetime.today().date():
        report_for_today = True
    else:
        report_for_today = False

    start_time = datetime(year=date.year, month=date.month, day=date.day, hour=0,
                          minute=0, second=0, microsecond=0, tzinfo=pytz.UTC)
    end_time = datetime(year=date.year, month=date.month, day=date.day, hour=23,
                        minute=59, second=59, microsecond=9999, tzinfo=pytz.UTC)

    # if daily_reports.count() > 0 and overwrite is False:
    #     __logger.warning('Daily report won\'t be generated because it already exists. ' + date)

    agents = UptimeAgent.objects.all()
    for agent in agents:
        existing_reports = UptimeReport.objects.filter(
            period='DAILY'
        ).filter(
            start_time=start_time,
            agent_key=agent.agent_key
        )

        if existing_reports.count() == 0:
            report = UptimeReport(agent_key=agent.agent_key, start_time=start_time, period='DAILY')
        elif existing_reports.count() == 1:
            report = existing_reports[0]
        elif existing_reports.count() > 1:
            raise Exception(
                "More than one daily report found within a day for the specified agent. Date: {0} Agent: {1}".format(
                    start_time.date(), agent.agent_key))
        missing_pings = 0

        ping_start_time = start_time
        ping_end_time = start_time + timedelta(minutes=UPTIME_PING_INTERVAL)

        while start_time.day == ping_start_time.day and ping_start_time < timezone.now():
            pings = UptimePing.objects.filter(
                agent_key=agent.agent_key
            ).filter(
                time__gte=ping_start_time,
                time__lt=ping_end_time
            )
            if pings.count() == 0:
                missing_pings = missing_pings + 1
            elif pings.count() > 1:
                __logger.warning(
                    'More than one ping found for the provided period {0} - {1}'.format(ping_start_time, ping_end_time))
            ping_start_time = ping_end_time
            ping_end_time = ping_end_time + timedelta(minutes=UPTIME_PING_INTERVAL)

        if report_for_today:
            covered_minutes = (timezone.now() - start_time).total_seconds() / 60.0
            report.end_time = datetime.now()
        else:
            covered_minutes = 1440.0
            report.end_time = end_time

        uptime = ((covered_minutes - (missing_pings * UPTIME_PING_INTERVAL)) / covered_minutes) * 100
        report.uptime_percentage = uptime
        report.save()


def generate_monthly_report(year, month, overwrite=False):
    if year < 1970 or month < 1 or month > 12:
        raise Exception("Invalid filters")

    end_day = monthrange(year, month)[1]
    if datetime.today().date().month == month:
        end_day = datetime.today().date().day

    agents = UptimeAgent.objects.all()
    for agent in agents:
        start_time = datetime(year=year, month=month, day=1, hour=0,
                              minute=0, second=0, microsecond=0, tzinfo=pytz.UTC)
        end_time = datetime(year=year, month=month, day=end_day, hour=23,
                            minute=59, second=59, microsecond=9999, tzinfo=pytz.UTC)
        daily_reports = UptimeReport.objects.filter(agent_key=agent.agent_key,
                                                    start_time__gte=start_time,
                                                    start_time__lte=end_time,
                                                    period='DAILY').order_by('start_time')

        sum_percentage = 0
        daily_percentages = [0] * end_day
        print('daily reports: {}'.format(daily_reports.count()))
        for report in daily_reports:
            if daily_percentages[report.start_time.day-1] != 0:
                __logger.error('Multiple daily reports found. Agent key: {0} Date: {1}'.format(report.agent_key,
                                                                                               report.start_time))
            else:
                daily_percentages[report.start_time.day-1] = report.uptime_percentage

        for i in daily_percentages:
            sum_percentage = sum_percentage + i

        monthly_uptime = sum_percentage / end_day
        monthly_reports = UptimeReport.objects.filter(agent_key=agent.agent_key,
                                                      start_time=start_time,
                                                      period='MONTHLY')
        if monthly_reports.count() == 0:
            monthly_report = UptimeReport(agent_key=agent.agent_key,
                                          start_time=start_time,
                                          end_time=end_time,
                                          period='MONTHLY',
                                          updated=datetime.now(),
                                          uptime_percentage=monthly_uptime,
                                          )
            monthly_report.save()
        elif monthly_reports.count() == 1:
            monthly_report = monthly_reports[0]
            monthly_report.uptime_percentage = monthly_uptime
            monthly_report.updated = datetime.now()
            monthly_report.save()
        else:
            raise Exception(
                "More than one monthly report found within a month for the specified agent. Date: {0} Agent: {1}".format(
                    start_time.date(), agent.agent_key))
