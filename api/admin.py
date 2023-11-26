from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import (MaxImpactFundGrant, Evaluation,
                     Allotment, Charity, Intervention, AllGrantsFundGrant)
from .admin_reordering import admin_site

class AllotmentInline(admin.StackedInline):
    model = Allotment
    extra = 1  # Set how many extra forms to display
    def get_formset(self, request, obj=None, **kwargs):
        '''Hide the foreign key fields for the alternative type of parent grant - only works for
        the 'change' view. For the 'add' view, see the respective GrantAdmin classes below.'''
        if isinstance(obj, MaxImpactFundGrant):
            self.exclude = ['all_grants_fund_grant']
        elif isinstance(obj, AllGrantsFundGrant):
            self.exclude = ['max_impact_fund_grant']
        return super(AllotmentInline, self).get_formset(request, obj, **kwargs)

class AllotmentAdmin(admin.ModelAdmin):
    readonly_fields = ('rounded_cents_per_output',)

    @admin.display(description='Rounded cents per output (not auto-refreshed)')
    def rounded_cents_per_output(self, allotment):
        return round(allotment.cents_per_output())

class EvaluationAdmin(admin.ModelAdmin):
    fields = (
        'charity', 'intervention', 'start_year', 'start_month',  'cents_per_output',
        'cents_per_output_upper_bound', 'cents_per_output_lower_bound', 'source_name',
        'source_url', 'comment')
    list_display = ('charity', 'start_year', 'start_month', 'intervention','cents_per_output')
    search_fields = ['charity__charity_name', 'charity__abbreviation',
                     'intervention__short_description', 'intervention__long_description',
                     'comment', 'source_name']
    list_filter = ['charity__abbreviation', 'intervention__short_description',
                   'start_month', 'start_year', 'source_name']

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
    def get_fieldsets(self, request, obj=None):
        '''Hide the foreign key fields for the alternative type(s) of parent grant when adding a new
        grant - only works for the 'add' view. For the 'change' view, see AllotmentInline class.'''
        if obj is None:
            self.inlines[0].exclude = ['all_grants_fund_grant']
        return super().get_fieldsets(request, obj)

class AllGrantsFundGrantAdmin(admin.ModelAdmin):
    inlines = [AllotmentInline]
    search_fields = ['allotment__charity__charity_name', 'allotment__charity__abbreviation',
        'allotment__intervention__short_description', 'allotment__intervention__long_description']
    list_filter = ['start_month', 'start_year', 'allotment__charity__abbreviation',
        'allotment__intervention__short_description']
    def get_fieldsets(self, request, obj=None):
        '''Hide the foreign key fields for the alternative type(s) of parent grant when adding a new
        grant - only works for the 'add' view. For the 'change' view, see AllotmentInline class.'''
        if obj is None:
            self.inlines[0].exclude = ['max_impact_fund_grant']
        return super().get_fieldsets(request, obj)

class CharityAdmin(admin.ModelAdmin):
    search_fields = ['charity_name', 'abbreviation']

admin_site.register(MaxImpactFundGrant, MaxImpactFundGrantAdmin)
admin_site.register(AllGrantsFundGrant, AllGrantsFundGrantAdmin)
admin_site.register(Evaluation, EvaluationAdmin)
admin_site.register(Charity, CharityAdmin)
admin_site.register(Intervention)
admin_site.register(Allotment, AllotmentAdmin)
