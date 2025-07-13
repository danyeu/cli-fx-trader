from datetime import datetime, timedelta
from decimal import Decimal
from logging import getLogger

from utils.currency import Currency
from utils.db import get_currency_owned, update_currencies

logger = getLogger(__name__)

# Seconds after FX rate quote at which the transaction timesout
quote_timeout: datetime = timedelta(seconds=10)

QUOTE_TIMEOUT_SECONDS: str = str(int(quote_timeout.total_seconds()))

class Transaction:
    """Represents a transaction exchanging one currency for another."""
    def __init__(self, currency_bought: Currency, currency_sold: Currency, fx_rate: Decimal = None, quote_time: datetime = datetime.now()):
        """Args:
            currency_bought (Currency): Currency to be bought.
            currency_sold (Currency): Currency to be sold.
            fx_rate (Decimal, optional): FX rate exchanged at. Used for __str__ only.
            quote_time (datetime, optional): Time FX rate was quoted. Defaults to current time.
        """
        self.b = currency_bought
        self.s = currency_sold
        self.fx_rate = fx_rate
        self.quote_time = quote_time
        self._validate_init()

    def _validate_init(self):
        if self.b.ccy == self.s.ccy:
            raise ValueError("Unexpected transaction of same CCY")

    def execute(self) -> bool:
        old_b = get_currency_owned(self.b.ccy)
        old_s = get_currency_owned(self.s.ccy)

        new_b = Currency(self.b.ccy, old_b.quantity + self.b.quantity)
        new_s = Currency(self.s.ccy, old_s.quantity - self.s.quantity)

        if update_currencies(self.b.ccy, new_b.quantity_str, self.s.ccy, new_s.quantity_str):
            return True

        logger.error("Error executing transaction.", exc_info=True)
        return False

    def expired(self) -> bool:
        if datetime.now() - self.quote_time > quote_timeout:
            return True
        return False

    def __str__(self):
        if self.fx_rate:
            return "{} {} @ {} => {} {}".format(
                self.s.ccy.name, self.s.quantity_str,
                self.fx_rate,
                self.b.ccy.name, self.b.quantity_str)
        return "{} {} => {} {}".format(
                self.s.ccy.name, self.s.quantity_str,
                self.b.ccy.name, self.b.quantity_str)

    def print(self):
        print(self)
