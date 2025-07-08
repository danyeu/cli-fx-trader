from decimal import Decimal
import os
import requests

from utils.currency import CCY, BASE_CURRENCY, FX_CURRENCY_NAMES
from utils.logger import LOGGER

RATES_URL = f"""https://openexchangerates.org/api/latest.json?app_id={os.getenv("OER_API_KEY")}&base={BASE_CURRENCY.name}&symbols={",".join(FX_CURRENCY_NAMES)}"""

def get_rates() -> dict[str, str]:
    response = requests.get(RATES_URL, timeout=10)
    data = response.json(parse_float=str)
    if response.status_code != 200:
        LOGGER.info("Error getting FX rates: %s: %s", response.status_code, response.text)
        raise ConnectionError("Error getting FX rates")

    if "rates" not in data:
        LOGGER.info("No \"rates\" in API response: %s", response.text)
        raise ConnectionError("Error getting FX rates")

    rates = data["rates"]
    return rates

def get_rate(ccy: CCY) -> Decimal:
    rates = get_rates()
    try:
        rate = rates[ccy.name]
    except KeyError:
        LOGGER.error("%s not found in returned rates.", ccy.name)
        return None
    return Decimal(rate)
