from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from currency_converter import CurrencyConverter
from datetime import date

def validate_year(value):
    '''Validate year between 2000 and now'''
    current_year = date.today().year
    if value not in range(2000,current_year + 1):
        raise ValidationError(
            _('must be the year of a Givewell evalution'),
            params={'value': value},
        )

def validate_month(value):
    '''Validate month is a number from 1-12'''
    if value not in range(1, 13):
        raise ValidationError(
            _('month must be a number from 1-12'),
            params={'value': value},
        )

class Charity(models.Model):
    '''Has many Evaluations and Allotments'''
    def __str__(self):
        return self.charity_name
    @classmethod
    def is_hidden_from_admin_sidebar(cls):
        return True
    charity_name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=10)
    class Meta:
        verbose_name_plural = 'Charities'

@receiver(pre_save, sender=Charity)
def capitalize_abbreviation(sender, instance, *args, **kwargs):
    instance.abbreviation = instance.abbreviation.upper()

class MaxImpactFundGrant(models.Model):
    '''Has many Allotments
    Unique by year + month'''
    def __str__(self):
        return f'{self.start_year}-{self.start_month}'
    @classmethod
    def is_hidden_from_admin_sidebar(cls):
        return False
    start_year = models.PositiveIntegerField(validators=[validate_year])
    start_month = models.PositiveIntegerField(validators=[validate_month])
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['start_year', 'start_month'], name='unique_date')]

class Intervention(models.Model):
    '''Has many Evaluations and Allotments
    Unique by short description'''
    def __str__(self):
        return self.short_description
    @classmethod
    def is_hidden_from_admin_sidebar(cls):
        return False
    short_description = models.CharField(max_length=100)
    long_description = models.CharField(max_length=5000)
    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['short_description'], name='unique_short_description')]

class Allotment(models.Model):
    def __str__(self):
        return f"${self.sum_in_cents / 100} to {self.charity.charity_name}"
    def cents_per_output(self) -> str:
        return self.sum_in_cents / self.number_outputs_purchased
    max_impact_fund_grant = models.ForeignKey(MaxImpactFundGrant, on_delete=models.CASCADE)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.PROTECT)
    sum_in_cents = models.PositiveIntegerField()
    number_outputs_purchased = models.PositiveIntegerField()

class Evaluation(models.Model):
    '''Unique by year, month, and charity name'''
    def __str__(self):
        return f'{self.charity.charity_name} as of {self.start_year}-{self.start_month}'
    @classmethod
    def is_hidden_from_admin_sidebar(cls):
        return False
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.PROTECT)
    start_year = models.PositiveIntegerField(validators=[validate_year])
    start_month = models.PositiveIntegerField(validators=[validate_month])
    cents_per_output = models.PositiveIntegerField()
    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['charity', 'start_month', 'start_year'], name='unique_date_and_charity')]

