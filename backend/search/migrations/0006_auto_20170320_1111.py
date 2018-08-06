# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-20 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0005_auto_20161031_1021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='form',
            name='name',
            field=models.CharField(
                db_index=True, max_length=255, verbose_name='Form name'),
        ),
        migrations.AlterField(
            model_name='question',
            name='name',
            field=models.CharField(
                db_index=True, max_length=100, unique=True, verbose_name='Question Name'),
        ),
        migrations.AlterField(
            model_name='sitequestion',
            name='name',
            field=models.CharField(
                db_index=True, max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='sitequestion',
            name='text',
            field=models.TextField(
                db_index=True, null=True, verbose_name='Text'),
        ),
        migrations.AlterField(
            model_name='sitequestion',
            name='type',
            field=models.CharField(choices=[('integer', 'Integer'), ('text', 'Text'), ('checkbox', 'Checkbox'), ('yesno', 'Yes/No'), ('dropdown', 'Dropdown'), ('date_mdy', 'Date: MM/DD/YYYY'), ('date_dmy', 'Date: DD/MM/YYYY'), ('date_ymd', 'Date: YYYYY/MM/DD'), ('datetime_mdy', 'Datetime: MM/DD/YYYY HH:MM'), ('datetime_dmy', 'Datetime: DD/MM/YYYY HH:MM'), ('datetime_ymd', 'Datetime: YYYY/MM/DD HH:MM'), ('datetime_seconds_mdy', 'Datetime with seconds: MM/DD/YYYY HH:MM:SS'), ('datetime_seconds_dmy', 'Datetime with seconds: DD/MM/YYYY HH:MM:SS'), ('datetime_seconds_ymd', 'Datetime with seconds: YYYY/MM/DD HH:MM:SS'), ('email', 'Email'), ('alpha_only', 'Letters Only'), ('mrn_10d', 'MRN (10 digits)'), ('number', 'Number'), ('number_1dp', 'Number with 1 Decimal Place'),
                                            ('number_2dp', 'Number with 2 Decimal Place'), ('number_3dp', 'Number with 3 Decimal Place'), ('number_4dp', 'Number with 4 Decimal Place'), ('phone_australia', 'Phone - Australia'), ('phone', 'Phone'), ('postalcode_australia', 'Postal Code - Australia'), ('postalcode_canada', 'Postal Code - Canada'), ('ssn', 'Social Security Number - U.S.'), ('time', 'Time: HH:MM'), ('time_mm_ss', 'Time: MM:SS'), ('vmrn', 'Vanderbilt MRN'), ('zipcode', 'Zipcode - U.S.'), ('truefalse', 'True/False'), ('notes', 'Note'), ('description', 'Descipriton'), ('sql', 'SQL Field'), ('radio', 'Radio Button'), ('calc', 'Calculated Field'), ('matrix', 'Matrix'), ('descriptive', 'Descriptive')], db_index=True, max_length=24, null=True, verbose_name='Type'),
        ),
    ]