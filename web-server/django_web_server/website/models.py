from django.db import models
from datetime import datetime


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

    def __str__(self):
        return "Id: " + str(self.client_id) + \
               "First seen: " + self.first_seen_date + " " + self.first_seen_time + \
               "Last seen: " + self.last_seen_date + " " + self.last_seen_time
    
    def __get_time_since_seen_difference__(self):
        last_seen_str = self.last_seen_date + self.last_seen_time
        last_seen_datetime = datetime.strptime(last_seen_str, '%Y-%m-%d%H:%M:%S')
        now = datetime.now()
        difference = now - last_seen_datetime

        if now < last_seen_datetime:
            difference = datetime.timedelta(0)

        return difference
    
    def __get_time_since_first_connected_difference__(self):
        first_seen_str = self.first_seen_date + self.first_seen_time
        first_seen_datetime = datetime.strptime(first_seen_str, '%Y-%m-%d%H:%M:%S')
        now = datetime.now()
        difference = now - first_seen_datetime

        if now < first_seen_datetime:
            difference = datetime.timedelta(0)

        return difference

    def get_days_since_seen(self):
        difference = self.__get_time_since_seen_difference__()
        return difference.days

    def get_seconds_since_seen(self):
        difference = self.__get_time_since_seen_difference__()
        return difference.seconds
    
    def str_last_seen(self):
        difference = self.__get_time_since_seen_difference__()

        days = difference.days
        hours = difference.seconds // (60*60)
        minutes = (difference.seconds - hours*60*60) // 60
        seconds = difference.seconds - hours*60*60 - minutes*60

        result = ''
        if days > 0:
            result = str(days) + ' days'
        elif hours > 0:
            result = str(hours) + ' hours'
        elif minutes > 0:
            result = str(minutes) + ' minutes'
        else:
            result = 'now'

        return result

    def str_first_connected(self):
        difference = self.__get_time_since_first_connected_difference__()

        days = difference.days
        hours = difference.seconds // (60*60)
        minutes = (difference.seconds - hours*60*60) // 60
        seconds = difference.seconds - hours*60*60 - minutes*60

        result = ''
        if days > 0:
            result = str(days) + ' days'
        elif hours > 0:
            result = str(hours) + ' hours'
        elif minutes > 0:
            result = str(minutes) + ' minutes'
        else:
            result = 'now'

        return result



class SentTask(models.Model):
    id = models.AutoField(primary_key=True)
    task_id = models.CharField(max_length=200, default="")
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=60)
    status = models.CharField(max_length=60)
    task_type = models.CharField(max_length=20)
    task_info = models.CharField(max_length=100)

    def finished(self, time):
        self.finish_time = time

    def __str__(self):
        return ("task id = " + str(self.task_id) + " client id = " + str(self.client_id))
