# Generated by Django 3.2.12 on 2022-12-15 14:22

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('client_id', models.CharField(default='', max_length=50)),
                ('ip', models.CharField(default='', max_length=50)),
                ('os_name', models.CharField(default='', max_length=7)),
                ('os_version', models.CharField(default='', max_length=30)),
                ('hostname', models.CharField(default='', max_length=50)),
                ('host_user', models.CharField(default='', max_length=50)),
                ('privileges', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SentTask',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('task_id', models.CharField(default='', max_length=200)),
                ('start_time', models.CharField(max_length=60)),
                ('status', models.CharField(max_length=60)),
                ('task_type', models.CharField(max_length=20)),
                ('task_info', models.CharField(max_length=100)),
                ('task_output', jsonfield.fields.JSONField(default=dict)),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.client')),
            ],
        ),
    ]
