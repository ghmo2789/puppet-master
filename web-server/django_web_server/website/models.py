from django.db import models


# Create your models here.
class Client(models.Model):
    _id = models.CharField(max_length=50, primary_key=True, default="")
    ip = models.CharField(max_length=50, default="")
    os_name = models.CharField(max_length=7, default="")
    os_version = models.CharField(max_length=30, default="")
    hostname = models.CharField(max_length=50, default="")
    host_user = models.CharField(max_length=50, default="")
    privileges = models.CharField(max_length=50, default="")

    def __str__(self):
        return str(self.client_id)


class SentTask(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=60)
    finish_time = models.CharField(max_length=60)
    task_type = models.CharField(max_length=20)
    task_info = models.CharField(max_length=100)

    def finished(self, time):
        self.finish_time = time

    def __str__(self):
        return ("task id = " + str(self.id) + " client id = " + str(self.client_id))
