from datetime import date
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

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
        return f'Max Impact Fund Grant {self.start_year}-{self.start_month}'
    @classmethod
    def is_hidden_from_admin_sidebar(cls):
        return False
    start_year = models.PositiveIntegerField(validators=[validate_year])
    start_month = models.PositiveIntegerField(validators=[validate_month])
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['start_year', 'start_month'], name='unique_date')]

class AllGrantsFundGrant(models.Model):
    '''Has many Allotments
    Unique by year + month'''
    def __str__(self):
        return f'All Grants Fund Grant {self.start_year}-{self.start_month}'
    @classmethod
    def is_hidden_from_admin_sidebar(cls):
        return False
    start_year = models.PositiveIntegerField(validators=[validate_year])
    start_month = models.PositiveIntegerField(validators=[validate_month])
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['start_year', 'start_month'], name='unique_date_agf')]

class Intervention(models.Model):
    '''Has many Evaluations and Allotments
    Unique by short description'''
    def __str__(self):
        return self.short_description
    @classmethod
    def is_hidden_from_admin_sidebar(cls):
        return False
    short_description = models.CharField(max_length=100)
    long_description = models.CharField(max_length=1000)
    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['short_description'], name='unique_short_description')]

class Allotment(models.Model):
    '''Belongs to (a MaxImpactFundGrant or an AllGrantsFundGrant), and an Intervention and a Charity'''
    all_grants_fund_grant = models.ForeignKey(AllGrantsFundGrant,
                                        blank=True,
                                        null=True,
                                        on_delete=models.CASCADE)
    max_impact_fund_grant = models.ForeignKey(MaxImpactFundGrant,
                                              blank=True,
                                              null=True,
                                              on_delete=models.CASCADE)

    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.PROTECT)
    sum_in_cents = models.PositiveIntegerField()
    number_outputs_purchased = models.PositiveIntegerField()

    # Lower bound is mandatory but defaults to 0
    number_outputs_purchased_lower_bound = (models.PositiveIntegerField(default=0))

    # Upper bound is non-mandatory
    number_outputs_purchased_upper_bound = (models.PositiveIntegerField(null=True, blank=True))

    # The following fields can no value set, but if so will return an empty string
    source_name = models.TextField(blank=True)
    source_url = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    def clean(self):
        # Ensure that exactly one of all_grants_fund or max_impact_fund_grant is not null
        if (self.all_grants_fund_grant is None and self.max_impact_fund_grant is None) or \
           (self.all_grants_fund_grant is not None and self.max_impact_fund_grant is not None):
            raise ValidationError(
                'Must belong to either an all_grants_fund xor a max_impact_fund_grant (not both).'
            )
        # Validate number_outputs_purchased_lower_bound is less than number_outputs_purchased
        if self.number_outputs_purchased_lower_bound >= self.number_outputs_purchased:
            raise ValidationError({
                'number_outputs_purchased_lower_bound': (
                    'number_outputs_purchased_lower_bound must be less than number_outputs_purchased.'
                ),
            })
        # Validate number_outputs_purchased_upper_bound is greater than number_outputs_purchased
        # if it's set to a number
        if (self.number_outputs_purchased_upper_bound is not None) and (
            self.number_outputs_purchased_upper_bound <= self.number_outputs_purchased):
            raise ValidationError({
                'number_outputs_purchased_upper_bound': (
                    'number_outputs_purchased_upper_bound must be greater than number_outputs_purchased.'
                ),
            })
        super().clean()
    def __str__(self):
        return f"${self.sum_in_cents / 100} to {self.charity.charity_name}"
    def is_hidden_from_admin_sidebar(cls):
        return True
    def cents_per_output(self) -> str:
        return self.sum_in_cents / self.number_outputs_purchased
    def start_date(self) -> date:
        if self.max_impact_fund_grant:
            return date(
                self.max_impact_fund_grant.start_year,
                self.max_impact_fund_grant.start_month, 1)
        return date(
                self.all_grants_fund_grant.start_year,
                self.all_grants_fund_grant.start_month, 1)

class Evaluation(models.Model):
    '''Unique by year, month, and charity name'''
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.PROTECT)
    start_year = models.PositiveIntegerField(validators=[validate_year])
    start_month = models.PositiveIntegerField(validators=[validate_month])
    cents_per_output = models.PositiveIntegerField()
    cents_per_output_upper_bound = models.PositiveIntegerField(null=True, blank=True)
    cents_per_output_lower_bound = models.PositiveIntegerField(default=0)
    source_name = models.TextField(blank=True)
    source_url = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    def __str__(self):
        return f'{self.charity.charity_name} as of {self.start_year}-{self.start_month}'
    @classmethod
    def is_hidden_from_admin_sidebar(cls):
        return False
    def start_date(self) -> date:
        return date(self.start_year, self.start_month, 1)
    def clean(self):
        # Validate cents_per_output_lower_bound is less than cents_per_output
        if self.cents_per_output_lower_bound >= self.cents_per_output:
            raise ValidationError({
                'cents_per_output_lower_bound': (
                    'Cents per output lower bound must be less than cents per output.'
                ),
            })
        # Validate cents_per_output_upper_bound is greater than cents_per_output if it's set to
        # a number
        if (self.cents_per_output_upper_bound is not None) and (
            self.cents_per_output_upper_bound <= self.cents_per_output):
            raise ValidationError({
                'cents_per_output_upper_bound': (
                    'Cents per output upper bound must be greater than cents per output.'
                ),
            })
        super().clean()

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['charity', 'start_month', 'start_year'], name='unique_date_and_charity')]
