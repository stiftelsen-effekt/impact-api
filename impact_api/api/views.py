from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse # TODO: delete when unnecessary
from django.http import Http404 # TODO: delete when unnecessary
from .models import Evaluation, MaxImpactFundGrant, Charity
from datetime import date


def index(request):
    return HttpResponse("Hello, world. You're at the api index.")

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
    charity_abbreviations = [
        abbreviation.upper()
        for abbreviation in queries.getlist('charity_code', [])] or (
        Charity.objects.values_list('abbreviation', flat=True))
    start_year = queries.get('start_year') or 2000
    start_month = queries.get('start_month') or 1
    end_year = queries.get('end_year') or date.today().year
    end_month = queries.get('end_month') or date.today().month

    try:
        evaluations = Evaluation.objects.filter(
            charity__abbreviation__in=charity_abbreviations,
            start_year__gte=start_year,
            start_month__gte=start_month,
            start_year__lte=end_year,
            start_month__lte=end_month)

        response = { 'evaluations': [{
            key:value for key, value in evaluation.__dict__.items()
            if key not in ['_state']} for evaluation in evaluations] }
        # breakpoint()

    except Evaluation.DoesNotExist:
        response = {'error': 'No evaluation found with those parameters'}
    return JsonResponse(response)

def max_impact_fund_grant(request, year, month):
    try:
        distribution = MaxImpactFundGrant.objects.get(
            start_year=year,
            start_month=month)
    except MaxImpactFundGrant.DoesNotExist:
        raise Http404("No grant with those parameters")
    response = f"You're looking at this distribution {distribution}"
    return JsonResponse(response)
