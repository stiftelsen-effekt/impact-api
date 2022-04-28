from django.shortcuts import render
from django.http import HttpResponse
from .models import Evaluation
from datetime import date

def index(request):
    return HttpResponse("Hello, world. You're at the api index.")

def evaluation(request, charity_name, year):
    # e = Evaluation.get(charity_name=charity_name)
    start_date = date(year, 1, 1)
    evaluation = Evaluation.objects.get(
                                        charity_name=charity_name,
                                        start_date=start_date)
    response = f"You're looking at this evaluation {evaluation}"
    return HttpResponse(response)

def max_impact_distribution(request, year, month):
    pass
