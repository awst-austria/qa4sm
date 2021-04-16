from datetime import datetime, timedelta
from validator.models import UptimePing, UptimeReport, UptimeAgent
from validator.validation import pytz
from django.contrib.auth import get_user_model
from validator.uptime import generate_daily_report, generate_monthly_report, get_report
from django.test import TestCase

User = get_user_model()


class TestUptimeMethods(TestCase):
    test_agent_1 = 'test_agent_1'
    test_agent_2 = 'test_agent_2'

    def setUp(self):
        # Register test agent

        agent_1 = UptimeAgent(agent_key=self.test_agent_1, active=True)
        agent_1.save()

        agent_2 = UptimeAgent(agent_key=self.test_agent_2, active=True)
        agent_2.save()

        # Prepare test data
        # for 1983 October 100% uptime
        date = datetime(year=1983, month=10, day=1, hour=0, minute=0, microsecond=0, tzinfo=pytz.UTC)
        while date.month == 10:
            ping = UptimePing()
            ping.agent_key = agent_1.agent_key
            ping.time = date
            ping.save()
            date = date + timedelta(minutes=5)

        # for 1983 November 50% uptime
        date = datetime(year=1983, month=11, day=1, hour=0, minute=0, microsecond=0, tzinfo=pytz.UTC)
        while date.month == 11:
            ping = UptimePing()
            ping.agent_key = agent_1.agent_key
            ping.time = date
            ping.save()
            date = date + timedelta(minutes=10)

        # for 1983 January 50% uptime for test_agent_1, 100% uptime for test_agent_2
        date = datetime(year=1983, month=1, day=1, hour=0, minute=0, microsecond=0, tzinfo=pytz.UTC)
        while date.month == 1:
            ping = UptimePing()
            ping.agent_key = agent_1.agent_key
            ping.time = date
            ping.save()

            if date.minute % 10 == 0:
                ping = UptimePing()
                ping.agent_key = agent_2.agent_key
                ping.time = date
                ping.save()
            date = date + timedelta(minutes=5)
        print('pings: {}'.format(UptimePing.objects.all().count()))

    def test_get_report(self):

        # for this test we use the 1983 January "dataset". For this month we have pings from 2 different agents
        # agent_1 produced a ping every 5 minutes (100%), agent_2 every 10 minutes (50%)
        date = datetime(year=1983, month=1, day=1, hour=0, minute=0, microsecond=0, tzinfo=pytz.UTC)
        while date.month == 1:
            generate_daily_report(date)
            date = date + timedelta(days=1)

        daily_reports = UptimeReport.objects.filter(
            start_time__gte=datetime(year=1983, month=1, day=1, hour=0, minute=0, microsecond=0,
                                     tzinfo=pytz.UTC),
            start_time__lt=datetime(year=1983, month=2, day=1, hour=0, minute=0, microsecond=0,
                                    tzinfo=pytz.UTC),
            period='DAILY')

        assert daily_reports.count() == 62

        for report in daily_reports:
            if report.agent_key == self.test_agent_1:
                assert report.uptime_percentage == 100.0, 'Actual value: {}'.format(report.uptime_percentage)
            if report.agent_key == self.test_agent_2:
                assert report.uptime_percentage == 50.0, 'Actual value: {}'.format(report.uptime_percentage)

        generate_monthly_report(year=1983, month=1)
        monthly_reports = UptimeReport.objects.filter(
            start_time__gte=datetime(year=1983, month=1, day=1, hour=0, minute=0, microsecond=0,
                                     tzinfo=pytz.UTC),
            start_time__lt=datetime(year=1983, month=2, day=1, hour=0, minute=0, microsecond=0,
                                    tzinfo=pytz.UTC),
            period='MONTHLY')

        assert monthly_reports.count() == 2, 'Actual value: {}'.format(monthly_reports.count())
        for report in monthly_reports:
            if report.agent_key == self.test_agent_1:
                assert report.uptime_percentage == 100.0
            if report.agent_key == self.test_agent_2:
                assert report.uptime_percentage == 50.0

        daily_report = get_report('DAILY', datetime(year=1983, month=1, day=1, hour=0, minute=0, microsecond=0,
                                                    tzinfo=pytz.UTC))
        assert daily_report.uptime_percentage == 100.0

        monthly_report = get_report('MONTHLY', datetime(year=1983, month=1, day=1, hour=0, minute=0, microsecond=0,
                                                        tzinfo=pytz.UTC))
        assert monthly_report.uptime_percentage == 100.0

    def test_generate_daily_reports(self):

        # generate daily reports for 1983 October
        date = datetime(year=1983, month=10, day=1, hour=0, minute=0, microsecond=0, tzinfo=pytz.UTC)
        while date.month == 10:
            generate_daily_report(date)
            date = date + timedelta(days=1)

        daily_reports = UptimeReport.objects.filter(
            start_time__gte=datetime(year=1983, month=10, day=1, hour=0, minute=0, microsecond=0,
                                     tzinfo=pytz.UTC),
            start_time__lt=datetime(year=1983, month=11, day=1, hour=0, minute=0, microsecond=0,
                                    tzinfo=pytz.UTC),
            period='DAILY',
            agent_key=self.test_agent_1)

        # October has 31 days so we expect 31 daily reports
        assert daily_reports.count() == 31

        for report in daily_reports:
            # all of them should report 100% uptime
            assert report.uptime_percentage == 100.0

        # Generating monthly report
        generate_monthly_report(year=1983, month=10)
        monthly_reports = UptimeReport.objects.filter(
            start_time__gte=datetime(year=1983, month=10, day=1, hour=0, minute=0, microsecond=0,
                                     tzinfo=pytz.UTC),
            start_time__lt=datetime(year=1983, month=11, day=1, hour=0, minute=0, microsecond=0,
                                    tzinfo=pytz.UTC),
            period='MONTHLY',
            agent_key=self.test_agent_1)

        assert monthly_reports.count() == 1
        for report in monthly_reports:
            # all of them should report 100% uptime
            assert report.uptime_percentage == 100.0

        # Now let's do the same for 1983 November
        date = datetime(year=1983, month=11, day=1, hour=0, minute=0, microsecond=0, tzinfo=pytz.UTC)
        while date.month == 11:
            generate_daily_report(date)
            date = date + timedelta(days=1)

        daily_reports = UptimeReport.objects.filter(
            start_time__gte=datetime(year=1983, month=11, day=1, hour=0, minute=0, microsecond=0,
                                     tzinfo=pytz.UTC),
            start_time__lt=datetime(year=1983, month=12, day=1, hour=0, minute=0, microsecond=0,
                                    tzinfo=pytz.UTC),
            period='DAILY',
            agent_key=self.test_agent_1)

        # October has 31 days so we expect 31 daily reports
        assert daily_reports.count() == 30

        for report in daily_reports:
            # all of them should report 50% uptime
            assert report.uptime_percentage == 50.0

        # Generating monthly report
        generate_monthly_report(year=1983, month=11)
        monthly_reports = UptimeReport.objects.filter(
            start_time__gte=datetime(year=1983, month=11, day=1, hour=0, minute=0, microsecond=0,
                                     tzinfo=pytz.UTC),
            start_time__lt=datetime(year=1983, month=12, day=1, hour=0, minute=0, microsecond=0,
                                    tzinfo=pytz.UTC),
            period='MONTHLY',
            agent_key=self.test_agent_1)

        assert monthly_reports.count() == 1
        for report in monthly_reports:
            # all of them should report 100% uptime
            assert report.uptime_percentage == 50.0
