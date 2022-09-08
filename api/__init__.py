import urllib.request
import time
import sys
import os.path as op
from datetime import date, timedelta
from currency_converter import ECB_URL, CurrencyConverter


def get_refreshed_converter() -> CurrencyConverter:
    filename = f"currency_conversions/ecb_{date.today():%Y%m%d}.zip"

    if not op.isfile(filename):
        # If the next line raises an SSL error, following these steps might help:
        # https://stackoverflow.com/a/70495761/3210927
        urllib.request.urlretrieve(ECB_URL, filename)

    return CurrencyConverter(filename, True, True)


def get_currencies():
    return get_currency_converter().currencies


converter = get_refreshed_converter()


def get_currency_converter():
    global converter
    if converter is None:
        converter = get_refreshed_converter()
    return converter
