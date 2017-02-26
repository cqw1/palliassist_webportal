# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-21 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='category',
            field=models.CharField(choices=[(b'ESAS', b'ESAS'), (b'Pain', b'Pain'), (b'Medication', b'Medication'), (b'Other', b'Other')], default=b'Other', max_length=255),
        ),
    ]