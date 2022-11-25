from django.db import OperationalError
import django_filters
from .models import Client


class ClientFilter(django_filters.FilterSet):
    try:
        existing_os = list(Client.objects.values_list('os_name').distinct())
        CHOICES = tuple((i[0], i[0]) for i in existing_os)
        os_name = django_filters.ChoiceFilter(choices=CHOICES, empty_label="Select OS")
    except OperationalError as e:
        print("Database not initialized: " + str(e))
        print("Please run migrate, then makemigrations and migrate again")

    class Meta:
        model = Client
        fields = ('os_name',)
