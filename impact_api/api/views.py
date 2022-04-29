from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from .models import Evaluation, MaxImpactDistribution
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

def max_impact_distribution(request, year, month):
    try:
        distribution = MaxImpactDistribution.objects.get(
            start_year=year,
            start_month=month)
    except MaxImpactDistribution.DoesNotExist:
        raise Http404("No distribution with those parameters")
    response = f"You're looking at this distribution {distribution}"
    return HttpResponse(response)
