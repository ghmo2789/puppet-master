import django_filters
from .models import Client


class ClientFilter(django_filters.FilterSet):

    CHOICES = (
        ('mac', 'mac'),
        ('windows', 'windows'),
        ('linux', 'linux'),
    )

    os_name = django_filters.ChoiceFilter(choices=CHOICES, empty_label="Select OS")

    class Meta:
        model = Client
        fields = ('os_name',)
