import os.path as op
import urllib.request
from datetime import date, timedelta
from django.utils.translation import get_language
from rest_framework import serializers
from currency_converter import ECB_URL, CurrencyConverter, RateNotFoundError
from .models import Evaluation, MaxImpactFundGrant, Allotment, Intervention

class CurrencyManager():
    '''Deals with currency conversions

    #get_converted_value converts US cents to other currency specified in a context object
    #get_currency returns currency from a context object
    '''
    DEFAULT_LANGUAGE_CURRENCY_MAPPING = {
        'no': 'NOK',
        'en': 'USD'
    }

    def get_converted_value(self, context, original_value, conversion_date):
        '''Get latest currency conversions and return cost per output in
        specified currency, else in USD'''
        filename = f"currency_conversions/ecb_{date.today():%Y%m%d}.zip"

        if not op.isfile(filename):
            # If the next line raises an SSL error, following these steps might help:
            # https://stackoverflow.com/a/70495761/3210927
            urllib.request.urlretrieve(ECB_URL, filename)

        c = CurrencyConverter(filename)

        currency_code = (context.get('currency')
                         or self.DEFAULT_LANGUAGE_CURRENCY_MAPPING[get_language()]).upper()
        try:
            # ECB doesn't record conversion rates for weekend or some holiday dates, so if we don't
            # have a match, try again for the day four days earlier (to dodge around Easter weekend)
            return c.convert(
                original_value / 100,
                'USD',
                currency_code,
                conversion_date)
        except RateNotFoundError:
            return c.convert(
                original_value / 100,
                'USD',
                currency_code,
                conversion_date - timedelta(days=4))

    def get_currency(self, context):
        '''Return specified currency, else USD'''
        return (context.get('currency')
                or self.DEFAULT_LANGUAGE_CURRENCY_MAPPING[get_language()]).upper()

class InterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervention
        fields = ['long_description', 'short_description', 'id']

class EvaluationSerializer(serializers.ModelSerializer):
    intervention = InterventionSerializer(read_only=True)
    converted_cost_per_output = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    manager = CurrencyManager()

    def get_converted_cost_per_output(self, evaluation):
        '''Return cost per output in specified currency, else in USD'''
        conversion_date = evaluation.start_date()
        return self.manager.get_converted_value(self.context, evaluation.cents_per_output, conversion_date)

    def get_currency(self, evaluation):
        '''Return specified currency, else USD'''
        return self.manager.get_currency(self.context)

    def get_language(self, evaluation):
        '''Return globally set language'''
        return get_language()

    class Meta:
        model = Evaluation
        fields = '__all__'
        depth = 1

class AllotmentSerializer(serializers.ModelSerializer):
    intervention = InterventionSerializer(read_only=True)
    converted_sum = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    converted_cost_per_output = serializers.SerializerMethodField()

    manager = CurrencyManager()

    def get_converted_cost_per_output(self, allotment) -> str:
        '''Return cost per output in specified currency, else in USD'''
        return self.manager.get_converted_value(
            self.context, allotment.cents_per_output(), self._conversion_date(allotment))

    def get_converted_sum(self, allotment):
        '''Return sum in specified currency, else in USD'''
        return self.manager.get_converted_value(
            self.context, allotment.sum_in_cents, self._conversion_date(allotment))

    def get_currency(self, allotment):
        '''Return specified currency, else USD'''
        return self.manager.get_currency(self.context)

    def _conversion_date(self, allotment) -> date:
        return allotment.start_date()

    class Meta:
        model = Allotment
        exclude = ['max_impact_fund_grant']
        depth = 1

class MaxImpactFundGrantSerializer(serializers.ModelSerializer):
    allotment_set = AllotmentSerializer(many=True)
    language = serializers.SerializerMethodField()

    def get_language(self, allotment):
        '''Return globally set language'''
        return get_language()

    class Meta:
        model = MaxImpactFundGrant
        fields = '__all__'
