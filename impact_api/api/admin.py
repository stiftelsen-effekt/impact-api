from django.contrib import admin

from .models import (MaxImpactFundGrant, Evaluation,
                     Allotment, Charity, Intervention)

# class InterventionInline(admin.TabularInline):
#     model = Intervention

class AllotmentInline(admin.StackedInline):
    model = Allotment
    # TODO - Does adding the choice line do anything?

class EvaluationAdmin(admin.ModelAdmin):
    # TODO - Figure out how to add charity name
    list_display = (
        'charity', 'start_year', 'start_month', 'intervention', 'cents_per_output', )
    search_fields = []

    @admin.display(ordering='charity__charity_name', description='Charity')
    def charity(self, evaluation):
        return evaluation.charity.charity_name

    @admin.display(ordering='intervention__short_output_description',
                   description='Intervention')
    def intervention(self, evaluation):
        return evaluation.intervention.short_output_description

class MaxImpactFundGrantAdmin(admin.ModelAdmin):
    inlines = [AllotmentInline]
    search_fields = []

# class AllotmentAdmin(admin.ModelAdmin):
#     inlines = [InterventionInline]

class CharityAdmin(admin.ModelAdmin):
    search_fields = ['charity_name', 'abbreviation']

admin.site.register(MaxImpactFundGrant, MaxImpactFundGrantAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Charity, CharityAdmin)
admin.site.register(Intervention)

# Register your models here.
