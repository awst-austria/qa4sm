import logging
from calendar import monthrange

import pytz
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from valentina.settings import UPTIME_PING_INTERVAL
from validator.models import UptimeReport, UptimePing, UptimeAgent
from datetime import datetime, timedelta

__logger = logging.getLogger(__name__)


def generate_daily_report(date):
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

    if date > datetime.now(tz=pytz.UTC):
        raise Exception('Report cannot be generated for a future date')

    if date.date() == datetime.now(tz=pytz.UTC).date():
        report_for_today = True
    else:
        report_for_today = False

    start_time = datetime(year=date.year, month=date.month, day=date.day, tzinfo=pytz.UTC)
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

        downtime = missing_pings * UPTIME_PING_INTERVAL
        uptime = ((covered_minutes - downtime) / covered_minutes) * 100

        report.uptime_percentage = uptime
        report.downtime_minutes = downtime
        report.save()


def get_daily_reports(date=datetime.now(tz=pytz.UTC).date()):
    """
    Get daily reports for all agents
    Parameters
    ----------
    date

    Returns
    -------

    """
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        raise Exception("Input date should be time zone aware")

    return UptimeReport.objects.filter(
        start_time__gte=datetime(year=date.year, month=date.month, day=date.day),
        start_time__lt=datetime(year=date.year, month=date.month, day=date.day) + timedelta(days=1),
        period='DAILY').order_by('start_time')


def get_report(period, date=datetime.now(tz=pytz.UTC).date()):
    """
    Return report with the highest uptime for the specified date and period.
    Parameters
    ----------
    period Either DAILY ar MONTHLY
    date Start date of the period

    Returns
    -------

    """

    if period is None or (period != 'DAILY' and period != 'MONTHLY'):
        raise Exception("Period should be either DAILY or MONTHLY")

    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        raise Exception("Input date should be time zone aware")

    start_date = datetime(year=date.year, month=date.month, day=date.day)
    if period == 'MONTHLY':
        start_date = datetime(year=date.year, month=date.month, day=1)

    daily_reports = UptimeReport.objects.filter(
        start_time=start_date,
        period=period).order_by('start_time')

    report_to_return = None

    for report in daily_reports:
        if report_to_return is None or report.uptime_percentage > report_to_return.uptime_percentage:
            report_to_return = report

    return report_to_return


def generate_monthly_report(year, month):
    if year < 1970 or month < 1 or month > 12:
        raise Exception("Invalid filters")

    end_day = monthrange(year, month)[1]
    if datetime.now(tz=pytz.UTC).date().month == month:
        end_day = datetime.now(tz=pytz.UTC).date().day

    agents = UptimeAgent.objects.all()
    for agent in agents:
        start_time = datetime(year=year, month=month, day=1, tzinfo=pytz.UTC)
        end_time = datetime(year=year, month=month, day=end_day, hour=23,
                            minute=59, second=59, microsecond=9999, tzinfo=pytz.UTC)
        daily_reports = UptimeReport.objects.filter(agent_key=agent.agent_key,
                                                    start_time__gte=start_time,
                                                    start_time__lte=end_time,
                                                    period='DAILY').order_by('start_time')

        sum_percentage = 0
        sum_downtime = 0
        daily_percentages = [0] * end_day
        daily_downtimes = [-1] * end_day
        for report in daily_reports:
            if daily_percentages[report.start_time.day - 1] != 0:
                __logger.error('Multiple daily reports found. Agent key: {0} Date: {1}'.format(report.agent_key,
                                                                                               report.start_time))
            else:
                daily_percentages[report.start_time.day - 1] = report.uptime_percentage
                daily_downtimes[report.start_time.day - 1] = report.downtime_minutes

        for i in daily_percentages:
            sum_percentage = sum_percentage + i

        for i in daily_downtimes:
            if i == -1:
                sum_downtime = -1
                break
            sum_downtime = sum_downtime + i

        monthly_uptime = sum_percentage / end_day
        monthly_reports = UptimeReport.objects.filter(agent_key=agent.agent_key,
                                                      start_time=start_time,
                                                      period='MONTHLY')
        if monthly_reports.count() == 0:
            monthly_report = UptimeReport(agent_key=agent.agent_key,
                                          start_time=start_time,
                                          end_time=end_time,
                                          period='MONTHLY',
                                          updated=datetime.now(tz=pytz.UTC),
                                          uptime_percentage=monthly_uptime,
                                          downtime_minutes=sum_downtime
                                          )
            monthly_report.save()
        elif monthly_reports.count() == 1:
            monthly_report = monthly_reports[0]
            monthly_report.uptime_percentage = monthly_uptime
            monthly_report.downtime_minutes = sum_downtime
            monthly_report.updated = datetime.now(tz=pytz.UTC)
            monthly_report.save()
        else:
            __logger.error(
                "generate_monthly_report - More than one monthly report found within a month for the specified agent. Date: {0} Agent: {1}".format(
                    start_time.date(), agent.agent_key))
            raise Exception(
                "generate_monthly_report - More than one monthly report found within a month for the specified agent. Date: {0} Agent: {1}".format(
                    start_time.date(), agent.agent_key))
