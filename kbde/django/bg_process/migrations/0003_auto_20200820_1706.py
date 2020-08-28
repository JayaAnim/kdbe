# Generated by Django 3.1 on 2020-08-20 17:06

from django.db import migrations, models


def update_id_field(apps, schema_editor):
    BgProcessModel = apps.get_model("kbde_django_bg_process", "BgProcessModel")
    BgProcessModel.objects.update(bg_process_id=models.F("id"))


class Migration(migrations.Migration):

    dependencies = [
        ('kbde_django_bg_process', '0002_bgprocessmodel_bg_process_id'),
    ]

    operations = [
        migrations.RunPython(update_id_field),
    ]