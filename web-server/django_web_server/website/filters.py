from django.db import OperationalError
import django_filters
from .models import Client, SentTask


class ClientFilter(django_filters.FilterSet):
    try:
        existing_os = list(Client.objects.values_list('os_name', flat=True))
        os_CHOICES = tuple((i, i) for i in existing_os)
        os_name = django_filters.AllValuesFilter(choices=os_CHOICES, empty_label="Filter by OS")

        existing_hosts = list(Client.objects.values_list('hostname', flat=True))
        host_CHOICES = tuple((i, i) for i in existing_hosts)
        hostname = django_filters.AllValuesFilter(choices=host_CHOICES, empty_label="Filter by host name")

        existing_is_online = list(Client.objects.values_list('is_online', flat=True))
        is_online_CHOICES = ((True, 'Online'), (False, 'Offline'))
        is_online = django_filters.ChoiceFilter(choices=is_online_CHOICES, empty_label="Filter status")
    except OperationalError as e:
        print("Database not initialized: " + str(e))
        print("Please run migrate, then makemigrations and migrate again")

    class Meta:
        model = Client
        fields = ('os_name', 'hostname', 'is_online')


class TaskFilter(django_filters.FilterSet):

    try:
        existing_id = list(SentTask.objects.values_list('client_id', flat=True))
        existing_ip = list(Client.objects.filter(id__in=existing_id).values_list('ip', flat=True))
        ip_CHOICES = tuple((i, i) for i in existing_ip)
        client_id__ip = django_filters.AllValuesFilter(choices=ip_CHOICES, empty_label="Filter by IP")

        existing_status = list(SentTask.objects.values_list('status', flat=True))
        status_CHOICES = tuple((i, i) for i in existing_status)
        status = django_filters.AllValuesFilter(choices=status_CHOICES, empty_label="Filter by status")

        existing_types = list(SentTask.objects.values_list('task_type', flat=True))
        type_CHOICES = tuple((i, i) for i in existing_types)
        task_type = django_filters.AllValuesFilter(choices=type_CHOICES, empty_label="Filter by task type")
    except OperationalError as e:
        print("Database not initialized: " + str(e))
        print("Please run migrate, then makemigrations and migrate again")

    class Meta:
        model = SentTask
        fields = ('client_id__ip', 'status', 'task_type')
