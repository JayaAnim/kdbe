# Generated by Django 3.1 on 2020-08-20 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kbde_django_location', '0006_auto_20200820_1646'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='point',
            name='id',
        ),
        migrations.AlterField(
            model_name='point',
            name='point_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
