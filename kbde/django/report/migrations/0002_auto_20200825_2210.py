# Generated by Django 2.2.2 on 2020-08-25 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kbde_django_report', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
