# Generated by Django 3.1.2 on 2020-10-20 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kbde_django_location', '0014_auto_20200825_2142'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='zip_code_last_4',
            new_name='zip_code_4',
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
