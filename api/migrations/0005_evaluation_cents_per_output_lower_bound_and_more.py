# Generated by Django 4.2.6 on 2023-10-13 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_intervention_long_description_et_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluation',
            name='cents_per_output_lower_bound',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='cents_per_output_upper_bound',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='source_name',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='source_url',
            field=models.TextField(blank=True),
        ),
    ]
