# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-27 15:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0007_auto_20170329_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitequestionchoice',
            name='choice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='site_question_choice', to='search.Choice'),
        ),
    ]
