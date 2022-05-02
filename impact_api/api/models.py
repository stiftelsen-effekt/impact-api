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

class Charity(models.Model):
    '''Has many Evaluations and Allotments'''
    def __str__(self):
        return self.charity_name
    charity_name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=10)
    class Meta:
        verbose_name_plural = 'Charities'

class MaxImpactFundGrant(models.Model):
    '''Has many Allotments'''
    def __str__(self):
        return f'{self.start_year}-{self.start_month}'
    start_year = models.IntegerField(validators=[validate_year])
    start_month = models.IntegerField(validators=[validate_month])
    # TODO make unique by date

class Allotment(models.Model):
    def __str__(self):
        return f"${self.sum_in_cents / 100} to {self.charity.charity_name}"
    # TODO add function to get output cost
    def calculated_cents_per_output(self) -> str:
        return self.sum_in_cents / self.number_outputs_purchased

    max_impact_fund_grant = models.ForeignKey(
        MaxImpactFundGrant, on_delete=models.CASCADE)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)

    sum_in_cents = models.IntegerField()
    number_outputs_purchased = models.IntegerField()
    short_output_description = models.CharField(max_length=100)
    long_output_description = models.CharField(max_length=5000)

class Evaluation(models.Model):
    def __str__(self):
        return f'{self.charity.charity_name} as of {self.start_year}-{self.start_month}'
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)

    start_year = models.IntegerField(validators=[validate_year])
    start_month = models.IntegerField(validators=[validate_month])
    cents_per_output = models.IntegerField()
    short_output_description = models.CharField(max_length=100)
    long_output_description = models.CharField(max_length=5000)
    # TODO - make Evaluations unique by (charity id and date)

@receiver(pre_save, sender=Charity)
def capitalize_abbreviation(sender, instance, *args, **kwargs):
    instance.abbreviation = instance.abbreviation.upper()

