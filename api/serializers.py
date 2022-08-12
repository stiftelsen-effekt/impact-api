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

    def get_converted_value(self, context, original_value, model_instance):
        '''Get latest conversion on relevant date and return cost per
        output in specified currency, else in USD'''
        return self._get_exchange_rate_and_date(
            context, model_instance, original_value)['converted_value']

    def get_actual_exchange_rate_date(self, context, model_instance):
        '''Get the actual date the currency was converted on, after
        adjusting for days where it wasn't available'''
        return self._get_exchange_rate_and_date(
            context, model_instance)['conversion_date']

    def _targeted_conversion_date(self, context, model_instance):
        if context.get('donation_year'):
            attempted_conversion_date = date(
                int(context.get('donation_year')),
                int(context.get('donation_month', 1)),
                int(context.get('donation_day', 1)))
        else:
            attempted_conversion_date = model_instance.start_date()
        return attempted_conversion_date


    def _get_exchange_rate_and_date(self, context, model_instance, original_value=1):
        filename = f"currency_conversions/ecb_{date.today():%Y%m%d}.zip"
        conversion_date = self._targeted_conversion_date(context, model_instance)

        if not op.isfile(filename):
            # If the next line raises an SSL error, following these steps might help:
            # https://stackoverflow.com/a/70495761/3210927
            urllib.request.urlretrieve(ECB_URL, filename)

        c = CurrencyConverter(filename)

        currency_code = (context.get('currency')
                         or self.DEFAULT_LANGUAGE_CURRENCY_MAPPING[get_language()]).upper()

        converted_value = None
        day_difference = 0
        while not converted_value:
            try:
                # ECB doesn't record conversion rates for weekend or some holiday dates, so if we
                # don't have a match, try again for the day four days earlier (to dodge around
                # Easter weekend)
                converted_value = c.convert(
                    original_value / 100,
                    'USD',
                    currency_code,
                    conversion_date - timedelta(day_difference))
            except RateNotFoundError:
                day_difference += 1
        return {'conversion_date': conversion_date - timedelta(day_difference),
                'converted_value': converted_value}


    def get_currency(self, context):
        '''Return specified currency, else USD'''
        return (context.get('currency')
                or self.DEFAULT_LANGUAGE_CURRENCY_MAPPING[get_language()]).upper()

class InterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervention
        fields = ['long_description', 'short_description', 'id']

class AllotmentSerializer(serializers.ModelSerializer):
    intervention = InterventionSerializer(read_only=True)
    converted_sum = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    converted_cost_per_output = serializers.SerializerMethodField()
    exchange_rate_date = serializers.SerializerMethodField()
    manager = CurrencyManager()

    def get_converted_cost_per_output(self, allotment) -> str:
        '''Return cost per output in specified currency, else in USD'''
        return self.manager.get_converted_value(
            self.context, allotment.cents_per_output(), allotment)

    def get_converted_sum(self, allotment):
        '''Return sum in specified currency, else in USD'''
        return self.manager.get_converted_value(
            self.context, allotment.sum_in_cents, allotment)

    def get_currency(self, allotment):
        '''Return specified currency, else USD'''
        return self.manager.get_currency(self.context)

    def get_exchange_rate_date(self, allotment):
        '''Return the actual date from which we're taking conversions'''
        return self.manager.get_actual_exchange_rate_date(
            self.context, allotment)

    class Meta:
        model = Allotment
        exclude = ['max_impact_fund_grant']
        depth = 1

class EvaluationSerializer(serializers.ModelSerializer):
    intervention = InterventionSerializer(read_only=True)
    converted_cost_per_output = serializers.SerializerMethodField()
    exchange_rate_date = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    manager = CurrencyManager()

    def get_converted_cost_per_output(self, evaluation):
        '''Return cost per output in specified currency, else in USD'''
        return self.manager.get_converted_value(
            self.context, evaluation.cents_per_output, evaluation)

    def get_exchange_rate_date(self, evaluation):
        '''Return the actual date from which we're taking conversions'''
        return self.manager.get_actual_exchange_rate_date(
            self.context, evaluation)

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

class MaxImpactFundGrantSerializer(serializers.ModelSerializer):
    allotment_set = AllotmentSerializer(many=True)
    language = serializers.SerializerMethodField()

    def get_language(self, grant):
        '''Return globally set language'''
        return get_language()

    class Meta:
        model = MaxImpactFundGrant
        fields = '__all__'
