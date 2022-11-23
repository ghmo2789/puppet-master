import django_filters
from .models import Client


class ClientFilter(django_filters.FilterSet):
    existing_os = list(Client.objects.values_list('os_name').distinct())
    CHOICES = tuple((i[0], i[0]) for i in existing_os)
    os_name = django_filters.ChoiceFilter(choices=CHOICES, empty_label="Select OS")

    class Meta:
        model = Client
        fields = ('os_name',)
