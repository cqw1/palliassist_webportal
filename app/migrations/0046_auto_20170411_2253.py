# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-12 03:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0045_painimages_container_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='painimages',
            options={'ordering': ('-created_date',)},
        ),
    ]
