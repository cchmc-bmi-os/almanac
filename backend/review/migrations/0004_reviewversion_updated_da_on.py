# Generated by Django 2.0.4 on 2018-05-22 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0003_auto_20170511_1110'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewversion',
            name='updated_da_on',
            field=models.DateTimeField(null=True),
        ),
    ]
