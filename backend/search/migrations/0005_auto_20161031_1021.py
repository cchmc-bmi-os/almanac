# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-31 10:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0004_userlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='name',
            field=models.CharField(
                max_length=100, unique=True, verbose_name='Question Name'),
        ),
    ]
