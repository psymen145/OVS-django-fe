# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-17 21:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectSurveillance', '0007_remove_workstep_phaseid'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectactivity',
            name='rowcreation',
            field=models.DateTimeField(auto_now_add=True, db_column='RowCreation', default=0),
            preserve_default=False,
        ),
    ]
