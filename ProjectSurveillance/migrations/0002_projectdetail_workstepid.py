# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-02 15:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectSurveillance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectdetail',
            name='workstepid',
            field=models.ForeignKey(db_column='WorkstepID', null=True, on_delete=django.db.models.deletion.CASCADE, to='ProjectSurveillance.Workstep'),
        ),
    ]
