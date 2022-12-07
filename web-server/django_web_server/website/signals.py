from django.db.models.signals import post_save
from notifications.signals import notify
from .models import SentTask, Client

def my_handler(sender, instance, created, **kwargs):
    notify.send(instance, verb='senttask saved')

post_save.connect(my_handler, sender=SentTask)