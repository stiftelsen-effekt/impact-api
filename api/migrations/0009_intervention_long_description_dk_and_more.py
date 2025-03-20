# Generated by Django 4.0.4 on 2025-03-20 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_intervention_long_description_sv_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='intervention',
            name='long_description_dk',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='intervention',
            name='short_description_dk',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='allotment',
            name='sum_in_cents',
            field=models.PositiveBigIntegerField(),
        ),
    ]
