from django.utils.translation import get_language
from rest_framework import serializers
from currency_converter import RateNotFoundError
from .models import Evaluation, MaxImpactFundGrant, Allotment, Intervention
from .__init__ import get_currency_converter
from datetime import date, timedelta


class CurrencyManager():
    '''Deals with currency conversions

    #converted_price converts US cents to other currency specified in a context object
    #currency returns currency from a context object
    '''
    DEFAULT_LANGUAGE_CURRENCY_MAPPING = {
        'no': 'NOK',
        'en': 'USD'
    }

    def converted_price(self, context, original_value, model_instance) -> float:
        '''Get latest conversion on relevant date and return cost per
        output in specified currency, else in USD. Fetches today's currency data
        from the ECB website if we don't already have it'''
        return self._converted_price_and_date(
            context, model_instance, original_value)['converted_value']

    def actual_exchange_rate_date(self, context, model_instance) -> date:
        '''Get the actual date the currency was converted on, after
        adjusting for days where it wasn't available. Fetches today's currency data
        from the ECB website if we don't already have it'''
        return self._converted_price_and_date(
            context, model_instance)['conversion_date']

    def currency(self, context) -> str:
        '''Return specified currency code, else USD'''
        return (context.get('currency')
                or self.DEFAULT_LANGUAGE_CURRENCY_MAPPING[get_language()]).upper()

    def _converted_price_and_date(self, context, model_instance, original_value=1) -> dict:

        conversion_date = self._targeted_conversion_date(
            context, model_instance)

        currency_code = (context.get('currency')
                         or self.DEFAULT_LANGUAGE_CURRENCY_MAPPING[get_language()]).upper()

        converted_value = get_currency_converter().convert(
            original_value / 100,
            'USD',
            currency_code,
            conversion_date)

        return {'conversion_date': conversion_date,
                'converted_value': converted_value}

    def _targeted_conversion_date(self, context, model_instance) -> date:
        if context.get('conversion_year'):
            attempted_conversion_date = date(
                int(context.get('conversion_year')),
                int(context.get('conversion_month', 1)),
                int(context.get('conversion_day', 1)))
        elif context.get('donation_year'):
            attempted_conversion_date = date(
                int(context.get('donation_year')),
                int(context.get('donation_month', 1)),
                int(context.get('donation_day', 1)))
        else:
            attempted_conversion_date = model_instance.start_date()
        return attempted_conversion_date


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
        return self.manager.converted_price(
            self.context, allotment.cents_per_output(), allotment)

    def get_converted_sum(self, allotment):
        '''Return sum in specified currency, else in USD'''
        return self.manager.converted_price(
            self.context, allotment.sum_in_cents, allotment)

    def get_currency(self, allotment):
        '''Return specified currency, else USD'''
        return self.manager.currency(self.context)

    def get_exchange_rate_date(self, allotment):
        '''Return the actual date from which we're taking conversions'''
        return self.manager.actual_exchange_rate_date(
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
        return self.manager.converted_price(
            self.context, evaluation.cents_per_output, evaluation)

    def get_exchange_rate_date(self, evaluation):
        '''Return the actual date from which we're taking conversions'''
        return self.manager.actual_exchange_rate_date(
            self.context, evaluation)

    def get_currency(self, evaluation):
        '''Return specified currency, else USD'''
        return self.manager.currency(self.context)

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
