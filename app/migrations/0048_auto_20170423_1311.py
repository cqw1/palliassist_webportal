# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-23 18:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0047_patient_esas_alert'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='telephone',
            field=models.TextField(default=b''),
        ),
        migrations.AlterField(
            model_name='patient',
            name='telephone',
            field=models.TextField(default=b''),
        ),
    ]