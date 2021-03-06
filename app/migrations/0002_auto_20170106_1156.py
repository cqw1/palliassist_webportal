# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-06 17:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('u_id', models.IntegerField()),
                ('full_name', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ('user_id',),
            },
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('u_id', models.IntegerField()),
                ('full_name', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ('user_id',),
            },
        ),
        migrations.AddField(
            model_name='doctor',
            name='patients',
            field=models.ManyToManyField(to='app.Patient'),
        ),
    ]
