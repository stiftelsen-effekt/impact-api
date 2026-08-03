import logging
import os
import os.path as op
import re
import ssl
import urllib.request
from datetime import date
from typing import Optional

import certifi
from currency_converter import ECB_URL, CurrencyConverter

logger = logging.getLogger(__name__)

CONVERSIONS_DIR = op.join(op.dirname(op.dirname(op.abspath(__file__))), "currency_conversions")
FILENAME_PATTERN = re.compile(r"^ecb_(\d{8})\.zip$")

converter = None


def download_rates(filename: str) -> None:
    # Use certifi's CA bundle rather than the system one: the ECB certificate
    # chains to a Sectigo root that is missing from older system CA bundles,
    # which otherwise fails with CERTIFICATE_VERIFY_FAILED.
    context = ssl.create_default_context(cafile=certifi.where())

    with urllib.request.urlopen(ECB_URL, context=context) as response:
        data = response.read()

    partial = f"{filename}.part"
    with open(partial, "wb") as file:
        file.write(data)
    os.replace(partial, filename)


def latest_local_rates() -> Optional[str]:
    names = [name for name in os.listdir(CONVERSIONS_DIR) if FILENAME_PATTERN.match(name)]
    if not names:
        return None
    return op.join(CONVERSIONS_DIR, max(names))


def get_refreshed_converter() -> CurrencyConverter:
    filename = op.join(CONVERSIONS_DIR, f"ecb_{date.today():%Y%m%d}.zip")

    if not op.isfile(filename):
        try:
            download_rates(filename)
        except Exception:
            # Serving slightly stale rates beats failing to boot at all.
            fallback = latest_local_rates()
            if fallback is None:
                raise
            logger.exception("Could not download ECB rates, falling back to %s", fallback)
            filename = fallback

    return CurrencyConverter(filename, True, True)


def get_currencies():
    return get_currency_converter().currencies


def get_currency_converter():
    global converter
    if converter is None:
        converter = get_refreshed_converter()
    return converter
