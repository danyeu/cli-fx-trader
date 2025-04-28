import re
from enum import Enum
from decimal import Decimal, ROUND_DOWN


class CCY(Enum):
    """Currencies with various attributes:
        int:     .dps        Number of decimal places allowed
        Decimal: .q          Pass as argument when quantising a Decimal of this CCY
        str:     .symbol     Currency symbol
        str:     .initial    Starting quantity for new users, defaults to 0
        """
    AUD = 1, 2, "AU$", "0"
    CAD = 2, 2, "CA$", "0"
    CHF = 3, 2, "SFr", "0"
    EUR = 4, 2, "€",   "0"
    GBP = 5, 2, "£",   "0"
    JPY = 6, 0, "¥",   "0"
    USD = 7, 2, "$",   "10000"

    def __new__(cls, value: str, dps: int, symbol: str, initial: str = "0"):
        obj = object.__new__(cls)
        obj._value_ = value # Unique index

        obj.dps     = dps
        obj.q       = Decimal("1" if dps == 0 else f"1.{dps * "0"}")
        obj.symbol  = symbol
        obj.initial = initial

        return obj

    @classmethod
    def from_string(cls, name: str):
        name = name.strip().upper()
        for c in CCY:
            if name == c.name:
                return c


BASE_CURRENCY = CCY.USD
FX_CURRENCIES: list[CCY] = [c for c in CCY if c != BASE_CURRENCY]
FX_CURRENCY_NAMES: list[str] = [c.name for c in FX_CURRENCIES]


def valid_quantity_sold(ccy: CCY, quantity: str) -> bool:
    """Returns whether the string quantity is valid amount of the specified currency to sell.
    Ensures quantity is positive and has no more decimal places than the currency allows.

        Args:
            quantity (str): The quantity traded as a string.
            ccy (CCY): The currency.
    """
    if ccy.dps == 0:
        return quantity.isdigit()
    if re.search(f"^\\d+(\\.\\d{{0,{ccy.dps}}}0*)?$", quantity) is None:
        return False
    if re.search(r"^0(\.0*)?$", quantity) is not None:
        return False
    return True

class Currency:
    """Represents a coupling of a certain quantity of currency.

    Args:
        ccy (CCY): CCY of Currency. Immutable.
        quantity (Decimal): Quantity of Currency. Should already be quantized to CCY's decimal places.
    """
    def __init__(self, ccy: CCY, quantity: Decimal):
        self._ccy: CCY = ccy
        self._name: str = ccy.name
        self._quantity: Decimal = None
        self.quantity: Decimal = quantity

    @property
    def ccy(self):
        return self._ccy

    @property
    def name(self):
        return self._name

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value: Decimal):
        # Precision of quantity must match exactly precision of CCY
        if -value.as_tuple().exponent != self.ccy.dps:
            raise ValueError(f"Quantity ({value}) doesn't match decimal places of currency ({self.ccy.dps})")
        self._quantity = value

    @property
    def quantity_str(self) -> str:
        """Returns quantity as string."""
        return str(self.quantity)

    @classmethod
    def from_string(self, ccy: CCY, quantity_str: str):
        """Returns Currency given a string quantity.
        Args:
            ccy (CCY): CCY of Currency.
            quantity_str (str): Quantity of Currency as string. Must not be more precise than CCY dps."""
        return Currency(ccy, Decimal(quantity_str).quantize(ccy.q))

    def to_base(self, fx_rate: Decimal):
        """Converts FX Currency to Base Currency object with fx_rate.

        Args:
            fx_rate (Decimal): The FX rate to be used.

        Returns:
            New Currency object in base currency.
        """
        if self.ccy == BASE_CURRENCY:
            raise NotImplementedError("Unexpected conversion of base to base")
        new_quantity = (self.quantity / fx_rate).quantize(BASE_CURRENCY.q, ROUND_DOWN)
        return Currency(BASE_CURRENCY, new_quantity)

    def to_fx(self, ccy: CCY, fx_rate: Decimal):
        """Converts Base Currency to FX Currency object with fx_rate.

        Args:
            fx_rate (Decimal): The FX rate to be used.

        Returns:
            New Currency object in base currency
        """
        if self.ccy != BASE_CURRENCY:
            raise NotImplementedError("Unexpected conversion of FX to FX")
        new_quantity = (self.quantity * fx_rate).quantize(ccy.q, ROUND_DOWN)
        return Currency(ccy, new_quantity)
