# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-22 23:16
from __future__ import unicode_literals

import app.models
import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_auto_20170222_1715'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=datetime.datetime.now)),
                ('file', models.FileField(upload_to=app.models.user_directory_path)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Patient')),
            ],
        ),
    ]
