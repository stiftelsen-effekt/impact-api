from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from django.utils.translation import activate
from currency_converter import CurrencyConverter

class QueriesMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # This code is executed just before the view is called
        queries = request.GET
        language = queries.get('language')
        currency = queries.get('currency')
        errors = []
        if currency and currency not in CurrencyConverter().currencies:
            errors.append(f'Currency {currency.upper()} not supported')
        if language and language.lower() not in [language[0] for language in settings.LANGUAGES]:
            errors.append(f'Language code {language} not supported')
        if errors:
            return JsonResponse({'errors': errors})
        if language and language.lower() in [language[0] for language in settings.LANGUAGES]:
            activate(language.lower())
