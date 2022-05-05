from django.contrib import admin

from .models import (MaxImpactFundGrant, Evaluation,
                     Allotment, Charity, Intervention)

class AllotmentInline(admin.StackedInline):
    model = Allotment
    # TODO - Does adding the choice line do anything?

class EvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'charity', 'start_year', 'start_month', 'intervention', 'cents_per_output', )
    search_fields = [
        'charity__charity_name', 'charity__abbreviation',
        'intervention__short_output_description',
        'intervention__long_output_description']
    # add_form = CustomUserCreationForm

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

# class AllotmentAdmin(admin.ModelAdmin):
#     inlines = [InterventionInline]

# class CustomUserAdmin(UserAdmin):
#     model = UserTrainer
#     add_form = CustomUserCreationForm
#     fieldsets = (
#         *UserAdmin.fieldsets,
#         (
#             'TrainerInfo',
#             {
#                 'fields': (
#                     'age', 'info', 'image', 'inst',
#                 )
#             }
#         )
#     )

# admin.site.register(UserTrainer, CustomUserAdmin)
# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     list_display = ('article', 'slug','trainer')
#     list_display_links = ('article',)
#     fields = ('article', 'slug', 'keywords', 'text',)
#     readonly_fields = ('trainer',)

#     def save_model(self, request, obj, form, change):
#         obj.trainer = request.user
#         super().save_model(request, obj, form, change)


class CharityAdmin(admin.ModelAdmin):
    search_fields = ['charity_name', 'abbreviation']

admin.site.register(MaxImpactFundGrant, MaxImpactFundGrantAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Charity, CharityAdmin)
admin.site.register(Intervention)

# Register your models here.
