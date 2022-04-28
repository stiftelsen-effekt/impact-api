from django.db import models

class MaxImpactDistribution(models.Model):
    def __str__(self):
        return f'{self.start_date}'
    start_date = models.DateField() # mandatory
    end_date = models.DateField(blank=True, null=True) # (not mandatory,
    # though maybe we want some validation that only one Distribution
    # lacks this); if present, must be after_start date

    # has_many Evaluations

class Evaluation(models.Model):
    def __str__(self):
        return f'{self.charity_name} starting {self.start_date}'
    max_impact_distribution = models.ForeignKey(
        MaxImpactDistribution, on_delete=models.CASCADE,
        blank=True, null=True)
    charity_name = models.CharField(max_length=200)
    start_date = models.DateField() # dates are mandatory unless it
    # belongs to a Distribution
    end_date = models.DateField(blank=True, null=True) # must be after start_date
    cents_per_output = models.IntegerField() # mandatory
    output_type = models.CharField(max_length=511)
    cents_donated = models.IntegerField(default=100) # only set
    # for Evaluations that belong to Distributions;

    # Evaluations are unique by (charity name and date/date range) - or
    # not if they might cover multiple interventions in the same year by
    # the same org
