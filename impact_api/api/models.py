from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

def validate_year(value):
    if value not in range(2000,2100):
        raise ValidationError(
            _('must be the year of a Givewell evalution'),
            params={'value': value},
        )

def validate_month(value):
    # TODO - find out best practice here. Move to a validators file?
    if value not in range(1, 13):
        raise ValidationError(
            _('month must be a number from 1-12'),
            params={'value': value},
        )

class MaxImpactDistribution(models.Model):
    def __str__(self):
        return f'{self.start_year}-{self.start_month}'
    start_year = models.IntegerField(validators=[validate_year])
    start_month = models.IntegerField(validators=[validate_month])
    # has_many Grants

class Grant(models.Model):
    def __str__(self):
        return f"${self.grant_in_cents / 100} to {self.charity_name}"
    max_impact_distribution = models.ForeignKey(
        MaxImpactDistribution, on_delete=models.CASCADE)
    charity_name = models.CharField(max_length=200)
    charity_abbreviation = models.CharField(
        max_length=10, blank=True, null=True)
    short_output_description = models.CharField(max_length=100)
    long_output_description = models.CharField(max_length=1000)
    grant_in_cents = models.IntegerField()
    number_outputs_purchased = models.IntegerField()

class Evaluation(models.Model):
    def __str__(self):
        return f'{self.charity_name} starting {self.start_year}-{self.start_month}'
    charity_abbreviation = models.CharField(max_length=10)
    charity_name = models.CharField(max_length=200)
    start_year = models.IntegerField(validators=[validate_year])
    start_month = models.IntegerField(validators=[validate_month])
    short_output_description = models.CharField(max_length=100)
    long_output_description = models.CharField(max_length=1000)
    cents_per_output = models.IntegerField()
    # TODO - make Evaluations unique by (charity name and date)

@receiver(pre_save, sender=Evaluation)
def capitalize_abbreviation(sender, instance, *args, **kwargs):
    instance.charity_abbreviation = instance.charity_abbreviation.upper()

