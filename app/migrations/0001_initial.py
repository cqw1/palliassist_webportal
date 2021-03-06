# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-31 23:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UnreadMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resolved', models.BooleanField(default=False)),
                ('patient_id', models.IntegerField()),
                ('patient_name', models.CharField(max_length=100)),
                ('num_unread', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
