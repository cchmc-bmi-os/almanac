# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-18 10:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('location', models.TextField()),
                ('started_at', models.DateTimeField()),
                ('status', models.CharField(choices=[
                 ('Grantee Review', 'Grantee Review'), ('Completed', 'Completed')], max_length=25)),
                ('completed_at', models.DateTimeField(null=True)),
                ('updated_da_summary', models.TextField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'review_review',
            },
        ),
        migrations.CreateModel(
            name='ReviewRole',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=25)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='review_role', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'review_review_role',
            },
        ),
        migrations.CreateModel(
            name='ReviewVersion',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('revision', models.IntegerField(default=1)),
                ('contents', models.TextField()),
                ('summary', models.TextField(null=True)),
                ('actions', models.TextField(null=True)),
                ('info', models.TextField(null=True)),
                ('is_locked', models.BooleanField(default=False)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='versions', to='review.Review')),
            ],
            options={
                'db_table': 'review_review_version',
            },
        ),
    ]
