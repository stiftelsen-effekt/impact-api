from modeltranslation.translator import translator, TranslationOptions
from .models import Intervention

# for Intervention model
class InterventionTranslationOptions(TranslationOptions):
    fields = ('short_description', 'long_description')

translator.register(Intervention, InterventionTranslationOptions)
