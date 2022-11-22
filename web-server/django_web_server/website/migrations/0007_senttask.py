# Generated by Django 4.1.3 on 2022-11-21 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_remove_client_id_alter_client_client_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='SentTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.PositiveIntegerField(default=0)),
                ('finish_time', models.PositiveIntegerField(default=0)),
                ('task_type', models.CharField(max_length=20)),
                ('task_info', models.CharField(max_length=100)),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.client')),
            ],
        ),
    ]
