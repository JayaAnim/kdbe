# Generated by Django 3.2.12 on 2023-03-27 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kbde_django_bg_process', '0004_auto_20200820_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='bgprocessmodel',
            name='bg_process_exception',
            field=models.TextField(blank=True, editable=False),
        ),
    ]
