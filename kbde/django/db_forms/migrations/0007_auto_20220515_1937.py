# Generated by Django 3.2.10 on 2022-05-15 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kbde_django_db_forms', '0006_auto_20220515_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='priority',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='field',
            name='priority',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
