from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('evaluations/<str:charity_name>/<int:year>/<int:month>', views.evaluation, name='evaluation'),
    path('distributions/<int:year>/<int:month>', views.max_impact_fund_grant, name='max_impact_fund_grant')
]
