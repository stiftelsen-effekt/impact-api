from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import (MaxImpactFundGrant, Evaluation,
                     Allotment, Charity, Intervention)

class AllotmentInline(admin.StackedInline):
    model = Allotment

class AllotmentAdmin(admin.ModelAdmin):
    readonly_fields = ('rounded_cents_per_output',)

    @admin.display(description='Rounded cents per output (not auto-refreshed)')
    def rounded_cents_per_output(self, allotment):
        return round(allotment.cents_per_output())

class EvaluationAdmin(admin.ModelAdmin):
    fields = (
        'charity', 'intervention',
        'start_year', 'start_month',  'cents_per_output')
    list_display = ('charity', 'start_year', 'start_month', 'intervention','cents_per_output')
    search_fields = ['charity__charity_name', 'charity__abbreviation',
                     'intervention__short_description', 'intervention__long_description']
    list_filter = ['charity__abbreviation', 'intervention__short_description',
                   'start_month', 'start_year']

    @admin.display(ordering='charity__charity_name', description='Charity')
    def charity(self, evaluation):
        return evaluation.charity.charity_name

    @admin.display(ordering='intervention__short_description',
                   description='Intervention')
    def intervention(self, evaluation):
        return evaluation.intervention.short_description

class MaxImpactFundGrantAdmin(admin.ModelAdmin):
    inlines = [AllotmentInline]
    search_fields = ['allotment__charity__charity_name', 'allotment__charity__abbreviation',
        'allotment__intervention__short_description', 'allotment__intervention__long_description']
    list_filter = ['start_month', 'start_year', 'allotment__charity__abbreviation',
        'allotment__intervention__short_description']

class CharityAdmin(admin.ModelAdmin):
    search_fields = ['charity_name', 'abbreviation']

admin.site.register(MaxImpactFundGrant, MaxImpactFundGrantAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Charity, CharityAdmin)
admin.site.register(Intervention)
admin.site.register(Allotment, AllotmentAdmin)

# Register your models here.



