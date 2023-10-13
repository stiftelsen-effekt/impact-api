from django.urls import path

from . import views

urlpatterns = [
    path('evaluations', views.evaluations, name='evaluations'),
    path('max_impact_fund_grants', views.max_impact_fund_grants, name='max_impact_fund_grants'),
    path('all_grants_fund_grants', views.all_grants_fund_grants, name='all_grants_fund_grants')
]
