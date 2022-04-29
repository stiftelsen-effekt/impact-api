from django.contrib import admin

from .models import MaxImpactDistribution, Evaluation

class EvaluationInline(admin.TabularInline):
    model = Evaluation
    choice = 5

class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('charity_name', 'start_year', 'start_month', 'cents_per_output', 'output_type')
    search_fields = ['charity_name', 'output_type']

class MaxImpactDistributionAdmin(admin.ModelAdmin):
    inlines = [EvaluationInline]


admin.site.register(MaxImpactDistribution, MaxImpactDistributionAdmin)
admin.site.register(Evaluation, EvaluationAdmin)

# Register your models here.
