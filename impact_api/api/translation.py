from modeltranslation.translator import translator, TranslationOptions
from .models import Intervention

# I found this guide to model translation library more helpful than the main docs:
# https://blog.devgenius.io/complete-guide-to-translation-django-model-fields-ed926a463689

# for Intervention model
class InterventionTranslationOptions(TranslationOptions):
    fields = ('short_description', 'long_description')

translator.register(Intervention, InterventionTranslationOptions)
