from django.db import models
from django.db.models import Model

# Create your models here.
class Client(models.Model):
    client_id = models.PositiveIntegerField(default=0, primary_key=True)
    os = models.CharField(max_length=7)
    version = models.PositiveIntegerField()
    host_name = models.CharField(max_length=50)
    host_user = models.CharField(max_length=50)
    status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.client_id) 


class SentTask(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=60)
    finish_time = models.CharField(max_length=60)
    task_type = models.CharField(max_length=20)
    task_info = models.CharField(max_length=100)

    def __str__(self):
        return ("task id = " + str(self.id) + " client id = " + str(self.client_id))