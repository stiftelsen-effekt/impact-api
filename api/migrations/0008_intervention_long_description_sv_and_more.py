# Generated by Django 4.0.4 on 2024-01-26 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_allotment_comment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='intervention',
            name='long_description_sv',
            field=models.CharField(max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name='intervention',
            name='short_description_sv',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
