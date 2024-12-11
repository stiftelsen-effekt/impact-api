from collections import namedtuple
from datetime import date
from typing import Callable
from django.http import JsonResponse
from django.db.models import Q
from .models import Evaluation, MaxImpactFundGrant, Charity, AllGrantsFundGrant
from .serializers import EvaluationSerializer, MaxImpactFundGrantSerializer, AllGrantsFundGrantSerializer
from .cache import datastore_cache
# Before any of the views are called, the code in middleware.py will run

@datastore_cache(timeout_days=1)
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
    conversion_year=<any year that ECB has data for>
    conversion_month=<1-12>
    conversion_day=<1-31. ECB data isn't comprehensive (missing weekends, for eg, so if the date
    doesn't match we'll decrement by day until it does>
    charity_abbreviation=AMF&charity_abbreviation=sci&charity_abbreviation=DtW
    The latter uses all supplied charity codes (and is case-insensitive for
    ascii characters)
    language=<i18n country code>
    currency=<ISO 4217 code>
    '''
    query_strings = request.GET
    charities_query = Q(
        charity__abbreviation__in=_charity_abbreviations(query_strings))
    response = _construct_response(
        query_strings=query_strings,
        model=Evaluation,
        model_description='evaluations',
        serializer=EvaluationSerializer,
        fetch_by_donation_func=_evaluations_by_donation_date,
        extra_queries=charities_query)
    return JsonResponse(response)

@datastore_cache(timeout_days=1)
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
    conversion_year=<any year that ECB has data for>
    conversion_month=<1-12>
    conversion_day=<1-31. ECB data isn't comprehensive (missing weekends, for eg, so if the date
    doesn't match we'll decrement by day until it does>
    language=<i18n country code>
    currency=<ISO 4217 code>
    '''
    query_strings = request.GET
    response = _construct_response(
        query_strings=query_strings,
        model=MaxImpactFundGrant,
        model_description='max_impact_fund_grants',
        serializer=MaxImpactFundGrantSerializer,
        fetch_by_donation_func=_grant_by_donation_date)
    return JsonResponse(response)

@datastore_cache(timeout_days=1)
def all_grants_fund_grants(request):
    '''Returns a Json response describing grants meeting parameters
    supplied as query strings. Parameters and behaviour are same as for max_impact_fund_grants
    '''
    query_strings = request.GET
    response = _construct_response(
        query_strings=query_strings,
        model=AllGrantsFundGrant,
        model_description='all_grants_fund_grants',
        serializer=AllGrantsFundGrantSerializer,
        fetch_by_donation_func=_grant_by_donation_date)
    return JsonResponse(response)

def _construct_response(query_strings, model: type, model_description: str, serializer: type,
                        fetch_by_donation_func: Callable, extra_queries=Q()) -> dict:
    lookup_dates = _get_lookup_dates(query_strings)
    if lookup_dates.donation_year:
        records = fetch_by_donation_func(model, lookup_dates, query_strings)
    else:
        records = _records(model, lookup_dates, extra_queries)

    response = {model_description: [
        serializer(record, context=query_strings).data for record in records]}
    if not records:
        response['warnings'] = [
            f'No {model_description} found with those parameters']
    return response


def _get_lookup_dates(query_strings) -> namedtuple:
    Dates = namedtuple(
        'Dates',
        'start_year start_month end_year end_month donation_year donation_month donation_day')
    return Dates(
        query_strings.get('start_year') or 2000,
        query_strings.get('start_month') or 1,
        query_strings.get('end_year') or date.today().year,
        query_strings.get('end_month') or 12,
        query_strings.get('donation_year'),
        query_strings.get('donation_month', 1),
        query_strings.get('donation_day', 1))


def _evaluations_by_donation_date(model, dates, query_strings) -> list:
    records = []

    for abbreviation in _charity_abbreviations(query_strings):
        single_charity_query = Q(charity__abbreviation=abbreviation)
        record = _record_by_donation_date(model, dates, single_charity_query)
        records += record
    return records


def _grant_by_donation_date(model, dates, _query_strings):
    return _record_by_donation_date(model, dates)


def _record_by_donation_date(model, dates, q3=Q()) -> list:
    try:
        q1 = Q(start_year=dates.donation_year,
               start_month__lte=dates.donation_month)
        q2 = Q(start_year__lt=dates.donation_year)
        result = [model.objects.filter((q1 | q2) & q3).order_by(
            '-start_year', '-start_month')[0]]
        return result
    except IndexError:
        return []


def _records(model, dates, extra_queries):
    return model.objects.filter(
        extra_queries,
        start_year__gte=dates.start_year,
        start_month__gte=dates.start_month,
        start_year__lte=dates.end_year,
        start_month__lte=dates.end_month)


def _charity_abbreviations(query_strings):
    return [abbreviation.upper()
            for abbreviation in query_strings.getlist('charity_abbreviation')] or (
                Charity.objects.values_list('abbreviation', flat=True))
