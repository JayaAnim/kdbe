# Generated by Django 3.1 on 2020-08-20 19:46

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kbde_django_location', '0010_auto_20200820_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='point',
            name='point',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326),
        ),
    ]
