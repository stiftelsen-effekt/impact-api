# Generated by Django 4.2.6 on 2023-10-13 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_allotment_number_outputs_purchased_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='intervention',
            name='long_description_et',
            field=models.CharField(max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name='intervention',
            name='short_description_et',
            field=models.CharField(max_length=100, null=True),
        ),
    ]