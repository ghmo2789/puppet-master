# Generated by Django 3.2.12 on 2022-12-14 15:13

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_alter_senttask_task_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='senttask',
            name='task_output',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
