# Generated by Django 2.2.2 on 2020-08-28 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kbde_django_db_import', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='importmappingrow',
            name='new_instance',
            field=models.BooleanField(default=True),
        ),
    ]
