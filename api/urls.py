from django.urls import path

from . import views

urlpatterns = [
    path('evaluations', views.evaluations, name='evaluations'),
    path('max_impact_fund_grants', views.max_impact_fund_grants, name='max_impact_fund_grants')
]
