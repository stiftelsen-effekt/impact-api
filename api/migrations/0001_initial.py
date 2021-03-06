# Generated by Django 4.0.4 on 2022-05-11 18:09

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Allotment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sum_in_cents', models.IntegerField()),
                ('number_outputs_purchased', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Charity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('charity_name', models.CharField(max_length=200)),
                ('abbreviation', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name_plural': 'Charities',
            },
        ),
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_year', models.IntegerField(validators=[api.models.validate_year])),
                ('start_month', models.IntegerField(validators=[api.models.validate_month])),
                ('cents_per_output', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Intervention',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_description', models.CharField(max_length=100)),
                ('long_description', models.CharField(max_length=5000)),
            ],
        ),
        migrations.CreateModel(
            name='MaxImpactFundGrant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_year', models.IntegerField(validators=[api.models.validate_year])),
                ('start_month', models.IntegerField(validators=[api.models.validate_month])),
            ],
        ),
        migrations.AddConstraint(
            model_name='maximpactfundgrant',
            constraint=models.UniqueConstraint(fields=('start_year', 'start_month'), name='unique_date'),
        ),
        migrations.AddConstraint(
            model_name='intervention',
            constraint=models.UniqueConstraint(fields=('short_description',), name='unique_short_description'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='charity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.charity'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='intervention',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.intervention'),
        ),
        migrations.AddField(
            model_name='allotment',
            name='charity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.charity'),
        ),
        migrations.AddField(
            model_name='allotment',
            name='intervention',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.intervention'),
        ),
        migrations.AddField(
            model_name='allotment',
            name='max_impact_fund_grant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.maximpactfundgrant'),
        ),
        migrations.AddConstraint(
            model_name='evaluation',
            constraint=models.UniqueConstraint(fields=('charity', 'start_month', 'start_year'), name='unique_date_and_charity'),
        ),
    ]
