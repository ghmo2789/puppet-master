# Generated by Django 4.1.3 on 2022-11-21 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_rename_verison_client_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
