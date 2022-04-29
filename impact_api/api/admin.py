from django.contrib import admin

from .models import MaxImpactDistribution, Evaluation, Grant

class GrantInline(admin.StackedInline):
    model = Grant
    choice = 5

class EvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'charity_name', 'start_year', 'start_month',
        'cents_per_output', 'short_output_description')
    search_fields = [
        'charity_name', 'short_output_description',
        'long_output_description']

class MaxImpactDistributionAdmin(admin.ModelAdmin):
    inlines = [GrantInline]
    search_fields = [
        'charity_name', 'short_output_description',
        'long_output_description']

admin.site.register(MaxImpactDistribution, MaxImpactDistributionAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Grant)

# Register your models here.
