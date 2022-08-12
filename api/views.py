from collections import namedtuple
from datetime import date
from typing import Callable
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import Evaluation, MaxImpactFundGrant, Charity
from .serializers import EvaluationSerializer, MaxImpactFundGrantSerializer

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
    donation_year=<any year, though will only return a non-empty result if >= earliest evaluation>
    donation_month=<1-12>
    donation_day=<1-31>
    charity_abbreviation=AMF&charity_abbreviation=sci&charity_abbreviation=DtW
    The latter uses all supplied charity codes (and is case-insensitive for
    ascii characters)
    language=<i18n country code>
    currency=<ISO 4217 code>
    '''
    query_strings = request.GET
    charities_query = Q(charity__abbreviation__in=_get_charity_abbreviations(query_strings))
    response = _construct_response(
        query_strings,
        Evaluation,
        'evaluations',
        EvaluationSerializer,
        _get_evaluations_by_donation_date,
        charities_query)
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
    donation_year=<any year, though will only return a non-empty result if >= earliest evaluation>
    donation_month=<1-12>
    donation_day=<1-31>
    language=<i18n country code>
    currency=<ISO 4217 code>
    '''

    query_strings = request.GET

    response = _construct_response(
        query_strings,
        MaxImpactFundGrant,
        'grants',
        MaxImpactFundGrantSerializer,
        _get_grant_by_donation_date)
    return JsonResponse(response)

def _construct_response(query_strings, klass: type, class_description: str, serializer, fetch_by_donation: Callable, extra_queries=Q()) -> dict:
    dates = _get_dates(query_strings)
    if dates.donation_year:
        records = fetch_by_donation(klass, dates, query_strings)
    else:
        records = _get_records(klass, dates, extra_queries)

    response = {class_description: [
        serializer(record, context=query_strings).data for record in records]}
    if not records:
        response['warnings'] = [f'No {class_description} found with those parameters']
    return response

def _get_dates(query_strings) -> namedtuple:
    Dates = namedtuple(
        'Dates', 'start_year start_month end_year end_month donation_year donation_month donation_day')
    return Dates(
        query_strings.get('start_year') or 2000,
        query_strings.get('start_month') or 1,
        query_strings.get('end_year') or date.today().year,
        query_strings.get('end_month') or 12,
        query_strings.get('donation_year'),
        query_strings.get('donation_month', 1),
        query_strings.get('donation_day', 1))

def _get_evaluations_by_donation_date(klass, dates, query_strings) -> list:
    records = []

    for abbreviation in _get_charity_abbreviations(query_strings):
        single_charity_query = Q(charity__abbreviation=abbreviation)
        try:
            record = _get_record_by_donation_date(klass, dates, single_charity_query)
            records += record
        except IndexError:
            pass
    return records

def _get_grant_by_donation_date(klass, dates, _query_strings):
    return _get_record_by_donation_date(klass, dates)

def _get_record_by_donation_date(klass, dates, q3=Q()) -> list:
    q1 = Q(start_year=dates.donation_year, start_month__lte=dates.donation_month)
    q2 = Q(start_year__lt=dates.donation_year)
    return [klass.objects.filter(
        (q1 | q2) & q3).order_by('-start_month', '-start_year')[0]]

def _get_records(klass, dates, extra_queries):
    return klass.objects.filter(
        extra_queries,
        start_year__gte=dates.start_year,
        start_month__gte=dates.start_month,
        start_year__lte=dates.end_year,
        start_month__lte=dates.end_month)

def _get_charity_abbreviations(query_strings):
    return [abbreviation.upper()
            for abbreviation in query_strings.getlist('charity_abbreviation')] or (
                Charity.objects.values_list('abbreviation', flat=True))
