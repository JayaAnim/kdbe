# Generated by Django 2.2.5 on 2020-01-02 19:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kbde_django_location', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='address',
            name='longitude',
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('locations', models.ManyToManyField(to='kbde_django_location.Location')),
            ],
            options={
                'unique_together': {('name', 'longitude', 'latitude')},
            },
        ),
        migrations.AddField(
            model_name='address',
            name='point',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='kbde_django_location.Point'),
        ),
    ]