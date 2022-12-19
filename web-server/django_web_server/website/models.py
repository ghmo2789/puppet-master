from django.db import models
from datetime import datetime, timedelta, timezone


# Create your models here.
class Client(models.Model):
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
    last_seen_date = models.CharField(max_length=50, default="")
    last_seen_time = models.CharField(max_length=50, default="")
    is_online = models.BooleanField(default=False)
    time_since_last_seen = models.FloatField(default=0)

    def __str__(self):
        return "Id: " + str(self.client_id) + \
               "First seen: " + self.first_seen_date + " " + self.first_seen_time + \
               "Last seen: " + self.last_seen_date + " " + self.last_seen_time

    def str_last_seen(self):
        difference = int(self.time_since_last_seen)

        days = difference // (24*60*60)
        hours = (difference - days*24*60*60) // (60*60)
        minutes = (difference - days*24*60*60 - hours*60*60) // 60

        result = ''
        if days > 0:
            result = str(days) + ' days '
        elif hours > 0:
            result = str(hours) + ' hours '
        elif minutes > 0:
            result = str(minutes) + ' minutes '
        else:
            result = 'now'

        return result


class SentTask(models.Model):
    id = models.AutoField(primary_key=True)
    task_id = models.CharField(max_length=200, default="")
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=60)
    start_time_datetime = models.DateTimeField(blank=True, default=datetime.now)
    status = models.CharField(max_length=60)
    task_type = models.CharField(max_length=20)
    task_info = models.CharField(max_length=100)

    def finished(self, time):
        self.finish_time = time

    def time_since_started(self):
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
        return ("task id = " + str(self.task_id) + " client id = " + str(self.client_id))
