from django.shortcuts import render
from django.http import JsonResponse
from django.http import Http404
from .models import Evaluation, MaxImpactFundGrant
from datetime import date

def index(request):
    return HttpResponse("Hello, world. You're at the api index.")

def evaluation(request, charity_abbreviation, year, month):
    try:
        evaluation = Evaluation.objects.get(
            charity__abbreviation=charity_abbreviation.upper(),
            start_year=year,
            start_month=month)
    except Evaluation.DoesNotExist:
        raise Http404("No evaluation with those parameters")
    charity_data = {'charity_name': evaluation.charity.charity_name,
                    'charity_abbreviation': evaluation.charity.abbreviation}
    response = charity_data | {
        key:value for key, value in evaluation.__dict__.items()
        if key not in ['_state']}

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
