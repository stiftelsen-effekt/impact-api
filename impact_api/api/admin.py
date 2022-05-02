from django.contrib import admin

from .models import MaxImpactFundGrant, Evaluation, Allotment, Charity

class AllotmentInline(admin.StackedInline):
    model = Allotment
    # TODO - Does adding the choice line do anything?


class EvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'start_year', 'start_month',
        'cents_per_output', 'short_output_description')
    search_fields = [
        'short_output_description',
        'long_output_description']

class MaxImpactFundGrantAdmin(admin.ModelAdmin):
    # inlines = [AllotmentInline]
    search_fields = [
        'short_output_description',
        'long_output_description']

class CharityAdmin(admin.ModelAdmin):
    search_fields = ['charity_name', 'abbreviation']

admin.site.register(MaxImpactFundGrant, MaxImpactFundGrantAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Charity, CharityAdmin)
admin.site.register(Allotment)

# Register your models here.
