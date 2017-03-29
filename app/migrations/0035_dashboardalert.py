# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-29 02:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_pk', models.IntegerField(default=0)),
                ('category', models.CharField(choices=[(b'MEDICATION', b'MEDICATION'), (b'ESAS', b'ESAS')], default=b'MEDICATION', max_length=255)),
                ('patient', models.ManyToManyField(to='app.Patient')),
            ],
        ),
    ]
