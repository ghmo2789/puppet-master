# Generated by Django 4.1.3 on 2022-11-23 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                ("id", models.AutoField(default=0, primary_key=True, serialize=False)),
                ("client_id", models.CharField(default="", max_length=50)),
                ("ip", models.CharField(default="", max_length=50)),
                ("os_name", models.CharField(default="", max_length=7)),
                ("os_version", models.CharField(default="", max_length=30)),
                ("hostname", models.CharField(default="", max_length=50)),
                ("host_user", models.CharField(default="", max_length=50)),
                ("privileges", models.CharField(default="", max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="SentTask",
            fields=[
                ("task_id", models.AutoField(primary_key=True, serialize=False)),
                ("start_time", models.CharField(max_length=60)),
                ("finish_time", models.CharField(max_length=60)),
                ("task_type", models.CharField(max_length=20)),
                ("task_info", models.CharField(max_length=100)),
                (
                    "client_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="website.client"
                    ),
                ),
            ],
        ),
    ]