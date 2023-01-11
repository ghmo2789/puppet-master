from django.db import models
from datetime import datetime, timedelta, timezone


class Client(models.Model):
    """
    A Django model representing a Client
    """
    id = models.AutoField(primary_key=True)
    client_id = models.CharField(max_length=50, default="")
    ip = models.CharField(max_length=50, default="")
    os_name = models.CharField(max_length=7, default="")
    os_version = models.CharField(max_length=30, default="")
    hostname = models.CharField(max_length=50, default="")
    host_user = models.CharField(max_length=50, default="")
    privileges = models.CharField(max_length=50, default="")
    first_seen_date = models.CharField(max_length=50, default="")
    first_seen_time = models.CharField(max_length=50, default="")
    first_seen_datetime = models.DateTimeField(blank=True, default=datetime.now)
    last_seen_date = models.CharField(max_length=50, default="")
    last_seen_time = models.CharField(max_length=50, default="")
    is_online = models.BooleanField(default=False)
    time_since_last_seen = models.FloatField(default=0)

    def __str__(self):
        """
        Get the string representation of a client
        :return: the client represented as a string
        """
        return "Id: " + str(self.client_id)

    def first_seen_time_str(self):
        """
        Get the time when client was first seen as a string
        :return: string containing hour:minute:seconds of first seen
        """
        time = self.first_seen_datetime
        string = "%s:%s:%s" % (time.hour, time.minute, time.second)
        return string

    def str_last_seen(self):
        """
        Get string with information of when client was last seen
        :return: A string containing number of days, hours and minutes since
                 last seen or the string 'now' if client was seen less than 1 minute ago
        """
        difference = int(self.time_since_last_seen)

        days = difference // (24*60*60)
        hours = (difference - days*24*60*60) // (60*60)
        minutes = (difference - days*24*60*60 - hours*60*60) // 60

        result = ''
        if days > 0:
            result += str(days) + ' days '
        if hours > 0:
            result += str(hours) + ' hours '
        if minutes > 0:
            result += str(minutes) + ' minutes '
        if minutes <= 0:
            result = 'now'

        return result


class SentTask(models.Model):
    """
    A Django model representing a sent Task
    """
    id = models.AutoField(primary_key=True)
    task_id = models.CharField(max_length=200, default="")
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=60)
    start_time_datetime = models.DateTimeField(blank=True, default=datetime.now)
    status = models.CharField(max_length=60)
    task_type = models.CharField(max_length=20)
    task_info = models.CharField(max_length=100)

    def finished(self, time):
        """
        Set finished time
        :param time: timestamp when senttask was finished
        :side effects: Updates the finished_time field of a sent task
        """
        self.finish_time = time

    def start_time_str(self):
        """
        Get the start time of a sent task as a string
        :return: string containing hour:minute:seconds of start time
        """
        time = self.start_time_datetime
        string = "%s:%s:%s" % (time.hour, time.minute, time.second)
        return string

    def time_since_started(self):
        """
        Get string with information of time since task was started
        :return: A string containing number of days, hours and minutes since
                 task was started, or the string 'less than one minute' if start
                 time was less than one minute ago
        """
        utc_now = datetime.now(timezone.utc)
        now = utc_now + timedelta(hours=1)
        difference = now - self.start_time_datetime

        if now < self.start_time_datetime:
            difference = timedelta(0)

        days = difference.days
        hours = difference.seconds // (60*60)
        minutes = (difference.seconds - hours*60*60) // 60

        result = ''
        if days > 0:
            result = str(days) + ' days ' + str(hours) + ' hours ' + str(minutes) + ' minutes '
        elif hours > 0:
            result = str(hours) + ' hours ' + str(minutes) + ' minutes '
        elif minutes > 0:
            result = str(minutes) + ' minutes '
        else:
            result = ' less than one minute'

        return result

    def __str__(self):
        """
        Get string representation of a sent task
        :return: a sent task represented as a string
        """
        return ("task id = " + str(self.task_id))
