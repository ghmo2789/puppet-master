# Generated by Django 4.1.3 on 2022-12-20 09:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="first_seen_datetime",
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
    ]
