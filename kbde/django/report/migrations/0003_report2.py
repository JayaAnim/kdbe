# Generated by Django 3.1.4 on 2020-12-08 22:27

from django.db import migrations, models
import django.db.models.deletion
import kbde.django.report.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('kbde_django_report', '0002_auto_20200825_2210'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4)),
                ('bg_process_status', models.CharField(choices=[('new', 'New'), ('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='new', max_length=255)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('record_count', models.IntegerField(blank=True, null=True)),
                ('renderer_name', models.CharField(max_length=255)),
                ('records_complete', models.IntegerField(default=0)),
                ('result', models.FileField(blank=True, null=True, upload_to=kbde.django.report.models.get_report_upload_to)),
                ('time_started', models.DateTimeField(blank=True, null=True)),
                ('time_completed', models.DateTimeField(blank=True, null=True)),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_kbde_django_report.report2_set+', to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
    ]
