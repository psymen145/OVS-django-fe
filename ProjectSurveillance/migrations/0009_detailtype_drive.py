# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-21 16:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectSurveillance', '0008_projectactivity_rowcreation'),
    ]

    operations = [
        migrations.AddField(
            model_name='detailtype',
            name='drive',
            field=models.NullBooleanField(db_column='Drive'),
        ),
    ]