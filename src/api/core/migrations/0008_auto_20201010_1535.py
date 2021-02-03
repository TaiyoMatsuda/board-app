# Generated by Django 3.0.8 on 2020-10-10 06:35

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20200927_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 10, 6, 35, 47, 806505, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='introduction',
            field=models.TextField(blank=True, max_length=1000),
        ),
    ]
