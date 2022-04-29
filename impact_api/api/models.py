from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_year(value):
    if value not in range(2000,3000):
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

    end_year = models.IntegerField(blank=True, null=True, validators=[validate_year]) # TODO must be after start_date
    end_month = models.IntegerField(blank=True, null=True, validators=[validate_month]) # TODO (not mandatory,
    # though maybe we want some validation that only one Distribution
    # lacks this); if present, must be after_start date

    # has_many Evaluations

class Evaluation(models.Model):
    def __str__(self):
        return f'{self.charity_name} starting {self.start_year}-{self.start_month}'
    max_impact_distribution = models.ForeignKey(
        MaxImpactDistribution, on_delete=models.CASCADE,
        blank=True, null=True)
    charity_name = models.CharField(max_length=200)
    start_year = models.IntegerField(validators=[validate_year]) # TODO dates are mandatory unless it
    # belongs to a Distribution
    start_month = models.IntegerField(validators=[validate_month])

    end_year = models.IntegerField(blank=True, null=True, validators=[validate_year]) # TODO must be after start_date
    end_month = models.IntegerField(blank=True, null=True, validators=[validate_month])
    cents_per_output = models.IntegerField()
    output_type = models.CharField(max_length=511)
    cents_donated = models.IntegerField(default=100) # only set
    # for Evaluations that belong to Distributions;

    # Evaluations are unique by (charity name and date/date range) - or
    # not if they might cover multiple interventions in the same year by
    # the same org

