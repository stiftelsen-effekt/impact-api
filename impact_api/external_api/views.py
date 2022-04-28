from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the api index.")

# def read_evaluation(request, charity, start_date):

