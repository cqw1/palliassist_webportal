# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-17 06:50
from __future__ import unicode_literals

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20170204_1835'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='telephone',
            field=phonenumber_field.modelfields.PhoneNumberField(default=b'', max_length=128),
        ),
    ]
