# Generated by Django 3.2.10 on 2022-05-15 18:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kbde_django_db_forms', '0005_fieldgroup_priority'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='field',
            options={},
        ),
        migrations.AlterField(
            model_name='choice',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='field',
            name='form',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='kbde_django_db_forms.form'),
        ),
        migrations.AlterField(
            model_name='field',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='fieldgroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='fieldgroup',
            name='priority',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fieldvalue',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='filledform',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='form',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterUniqueTogether(
            name='field',
            unique_together={('form', 'name'), ('form', 'priority')},
        ),
        migrations.AlterUniqueTogether(
            name='fieldgroup',
            unique_together={('form', 'priority')},
        ),
    ]
