from collections import namedtuple
from datetime import date
from django.shortcuts import render
from django.http import JsonResponse
from .models import Evaluation, MaxImpactFundGrant, Charity
from .serializers import (
    InterventionSerializer, EvaluationSerializer, AllotmentSerializer, MaxImpactFundGrantSerializer)

# Before any of the views are called, the code in middleware.py will run

def evaluations(request):
    '''Returns a Json response describing evaluations meeting parameters
    supplied as query strings. If any of the parameters are unspecified, it
    assumes the most general case (e.g. all charities given no charity_abbreviations)

    Query strings of the following form are parsed:
    start_year=<2000-present>
    start_month=<1-12>
    end_year=<2000-present>
    end_month=<1-12>
    charity_abbreviation=AMF&charity_abbreviation=sci&charity_abbreviation=DtW
    The latter uses all supplied charity codes (and is case-insensitive for
    ascii characters)
    language=<i18n country code>
    currency=<ISO 4217 code>
    '''
    queries = request.GET
    dates = _get_dates(queries)

    charity_abbreviations = [
        abbreviation.upper()
        for abbreviation in queries.getlist('charity_abbreviation')] or (
            Charity.objects.values_list('abbreviation', flat=True))

    evaluations = Evaluation.objects.filter(
        charity__abbreviation__in=charity_abbreviations,
        start_year__gte=dates.start_year,
        start_month__gte=dates.start_month,
        start_year__lte=dates.end_year,
        start_month__lte=dates.end_month)

    response = {'evaluations': [
        EvaluationSerializer(evaluation, context=queries).data for evaluation in evaluations]}
    if not evaluations:
        response['warnings'] = ['No evaluations found with those parameters']
    return JsonResponse(response)

def max_impact_fund_grants(request):
    '''Returns a Json response describing grants meeting parameters
    supplied as query strings. If any of the parameters are unspecified, it
    assumes the most general case (e.g. grants up to the present day
    given no end date)

    Query strings of the following form are parsed:
    start_year=<2000-present>
    start_month=<1-12>
    end_year=<2000-present>
    end_month=<1-12>
    language=<i18n country code>
    currency=<ISO 4217 code>
    '''
    queries = request.GET
    dates = _get_dates(queries)

    grants = MaxImpactFundGrant.objects.filter(
        start_year__gte=dates.start_year,
        start_month__gte=dates.start_month,
        start_year__lte=dates.end_year,
        start_month__lte=dates.end_month)
    response = {'max_impact_fund_grants': [
        MaxImpactFundGrantSerializer(grant, context=queries).data for grant in grants]}
    if not grants:
        response['warnings'] = ['No grants found with those parameters']
    return JsonResponse(response)

def _get_dates(queries) -> dict:
    '''Fill in missing dates from the request query, defaulting to
    beginning of evaluations when start_dates are missing and present day
    when end dates are missing'''
    Dates = namedtuple(
        'Dates', 'start_year start_month end_year end_month')
    return Dates(
        queries.get('start_year') or 2000,
        queries.get('start_month') or 1,
        queries.get('end_year') or date.today().year,
        queries.get('end_month') or 12)


