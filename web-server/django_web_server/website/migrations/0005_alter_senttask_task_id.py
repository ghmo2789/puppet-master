# Generated by Django 3.2.12 on 2022-12-02 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_senttask_task_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='senttask',
            name='task_id',
            field=models.CharField(default='', max_length=200),
        ),
    ]