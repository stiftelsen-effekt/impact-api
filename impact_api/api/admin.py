from django.contrib import admin

from .models import (MaxImpactFundGrant, Evaluation,
                     Allotment, Charity, Intervention)

class AllotmentInline(admin.StackedInline):
    model = Allotment
    # TODO - Does adding the choice line do anything?

class EvaluationAdmin(admin.ModelAdmin):
    readonly_fields = ['long_description', 'charity_abbreviation']
    # pseudo-fields = 'long_description', 'charity_abbreviation',
    fields = (
        'charity', 'charity_abbreviation', 'intervention', 'long_description',
        'start_year', 'start_month',  'cents_per_output', )
    list_display = (
        'charity', 'start_year', 'start_month', 'intervention',
        'cents_per_output', )
    search_fields = [
        'charity__charity_name', 'charity__abbreviation',
        'intervention__short_output_description',
        'intervention__long_output_description']
    list_filter = ['charity__abbreviation',
        'intervention__short_output_description', 'start_month',
        'start_year']
    @admin.display(description='Charity abbreviation')
    def charity_abbreviation(self, instance):
        return instance.charity.abbreviation

    @admin.display(description='Long description')
    def long_description(self, instance):
        return instance.intervention.long_output_description

    @admin.display(ordering='charity__charity_name', description='Charity')
    def charity(self, evaluation):
        return evaluation.charity.charity_name

    @admin.display(ordering='intervention__short_output_description',
                   description='Intervention')
    def intervention(self, evaluation):
        return evaluation.intervention.short_output_description

class MaxImpactFundGrantAdmin(admin.ModelAdmin):
    inlines = [AllotmentInline]
    search_fields = [
        'allotment__charity__charity_name',
        'allotment__charity__abbreviation',
        'allotment__intervention__short_output_description',
        'allotment__intervention__long_output_description',]
    list_filter = ['start_month', 'start_year',
        'allotment__charity__abbreviation',
        'allotment__intervention__short_output_description']

class CharityAdmin(admin.ModelAdmin):
    search_fields = ['charity_name', 'abbreviation']

admin.site.register(MaxImpactFundGrant, MaxImpactFundGrantAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Charity, CharityAdmin)
admin.site.register(Intervention)

# Register your models here.



