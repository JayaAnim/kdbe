# Generated by Django 3.2.12 on 2023-02-19 03:12

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Verification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4)),
                ('key_length', models.PositiveIntegerField(default=6)),
                ('key', models.CharField(blank=True, max_length=255)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('is_sent', models.BooleanField(default=False)),
                ('time_sent', models.DateTimeField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('time_completed', models.DateTimeField(blank=True, null=True)),
                ('time_valid', models.PositiveIntegerField(blank=True, default=600)),
                ('expire_time', models.DateTimeField(blank=True, null=True)),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_kbde_django_verification.verification_set+', to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='EmailVerification',
            fields=[
                ('verification_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='kbde_django_verification.verification')),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(default='Verification Code', max_length=255)),
                ('from_email', models.EmailField(blank=True, max_length=254)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('kbde_django_verification.verification',),
        ),
    ]
