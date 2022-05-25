from django.utils.translation import get_language
from rest_framework import serializers
from currency_converter import CurrencyConverter
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

    def get_converted_value(self, context, original_value):
        '''Return cost per output in specified currency, else  in USD'''
        currency_code = (context.get('currency')
                         or self.DEFAULT_LANGUAGE_CURRENCY_MAPPING[get_language()]).upper()
        return CurrencyConverter().convert(original_value / 100, 'USD', currency_code)

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
        '''Return cost per output in specified currency, else  in USD'''
        return self.manager.get_converted_value(self.context, evaluation.cents_per_output)

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
        return self.manager.get_converted_value(self.context, allotment.cents_per_output())

    def get_converted_sum(self, allotment):
        '''Return sum in specified currency, else in USD'''
        return self.manager.get_converted_value(self.context, allotment.sum_in_cents)

    def get_currency(self, allotment):
        '''Return specified currency, else USD'''
        return self.manager.get_currency(self.context)

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
