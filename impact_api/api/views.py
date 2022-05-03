from collections import namedtuple
from datetime import date
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import serializers
from .models import Evaluation, MaxImpactFundGrant, Charity, Allotment

# TODO - find out best practice on where to store serializer classes
class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'
        depth = 1

class AllotmentSerializer(serializers.ModelSerializer):
    cents_per_output = serializers.ReadOnlyField(
        source='rounded_cents_per_output')

    class Meta:
        model = Allotment
        exclude = ['max_impact_fund_grant']
        depth = 1

class MaxImpactFundGrantSerializer(serializers.ModelSerializer):
    allotment_set = AllotmentSerializer(many=True)
    class Meta:
        model = MaxImpactFundGrant
        fields = '__all__'

def evaluations(request):
    '''Returns a Json response describing evaluations meeting parameters
    supplied as query strings. If any of the parameters are unspecified, it
    assumes the most general case (e.g. all charities given no charity_codes)

    Query strings of the following form are parsed:
    start_year=integer
    start_month=integer
    end_year=integer
    end_month=integer
    charity_code=AMF&charity_code=sci&charity_code=DtW
    The latter uses all supplied charity codes (and is case-insensitive for
    ascii characters)
    '''
    queries = request.GET
    dates = get_dates(queries)
    charity_abbreviations = [
        abbreviation.upper()
        for abbreviation in queries.getlist('charity_code')] or (
        Charity.objects.values_list('abbreviation', flat=True))

    try:
        evaluations = Evaluation.objects.filter(
            charity__abbreviation__in=charity_abbreviations,
            start_year__gte=dates.start_year,
            start_month__gte=dates.start_month,
            start_year__lte=dates.end_year,
            start_month__lte=dates.end_month)

        response = {'evaluations': [
            EvaluationSerializer(evaluation).data for evaluation in evaluations]}

    except Evaluation.DoesNotExist:
        response = {'error': 'No evaluation found with those parameters'}
    return JsonResponse(response)

def max_impact_fund_grant(request):
    '''Returns a Json response describing grants meeting parameters
    supplied as query strings. If any of the parameters are unspecified, it
    assumes the most general case (e.g. grants up to the present day
    given no end date)

    Query strings of the following form are parsed:
    start_year=integer
    start_month=integer
    end_year=integer
    end_month=integer
    '''
    queries = request.GET
    dates = get_dates(queries)

    try:
        grants = MaxImpactFundGrant.objects.filter(
            start_year__gte=dates.start_year,
            start_month__gte=dates.start_month,
            start_year__lte=dates.end_year,
            start_month__lte=dates.end_month)
        response = { 'grants': [
            MaxImpactFundGrantSerializer(grant).data for grant in grants]}

    except MaxImpactFundGrant.DoesNotExist:
        response = {'error': 'No grant found with those parameters'}

    return JsonResponse(response)

def get_dates(queries) -> dict:
    '''Fill in missing dates from the request query, defaulting to
    beginning of evaluations when start_dates are missing and present day
    when end dates are missing'''
    Dates = namedtuple(
        'Dates', 'start_year start_month end_year end_month')
    return Dates(
        queries.get('start_year') or 2000,
        queries.get('start_month') or 1,
        queries.get('end_year') or date.today().year,
        queries.get('end_month') or date.today().month)



