from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from .models import Evaluation, MaxImpactFundGrant
from datetime import date

def index(request):
    return HttpResponse("Hello, world. You're at the api index.")

def evaluation(request, charity_name, year, month):
    try:
        evaluation = Evaluation.objects.get(
            charity_name=charity_name,
            start_year=year,
            start_month=month)
    except Evaluation.DoesNotExist:
        raise Http404("No evaluation with those parameters")
    response = f"You're looking at this evaluation {evaluation}"
    return HttpResponse(response)

def max_impact_fund_grant(request, year, month):
    try:
        distribution = MaxImpactFundGrant.objects.get(
            start_year=year,
            start_month=month)
    except MaxImpactFundGrant.DoesNotExist:
        raise Http404("No grant with those parameters")
    response = f"You're looking at this distribution {distribution}"
    return HttpResponse(response)
