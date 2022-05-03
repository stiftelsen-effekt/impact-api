from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('evaluations', views.evaluations, name='evaluations'),
    path('max_impact_fund_grants/<int:year>/<int:month>', views.max_impact_fund_grant, name='max_impact_fund_grant')
]
