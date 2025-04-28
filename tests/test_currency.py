import pytest
from decimal import Decimal
from fx_trader.currency import *

currencies = [c for c in CCY]

@pytest.mark.parametrize("ccy", currencies)
def test_dps(ccy):
    assert isinstance(ccy.dps, int)
    assert ccy.dps >= 0

@pytest.mark.parametrize("ccy", currencies)
def test_q(ccy):
    assert isinstance(ccy.q, Decimal)
    assert ccy.dps >= 0

@pytest.mark.parametrize("ccy", currencies)
def test_initial(ccy):
    assert isinstance(ccy.initial, str)

    # Initial must be numeric and non-negative
    try:
        initial_float = float(ccy.initial)
    except ValueError:
        assert False, f"initial amount of {ccy.name} isn't a number"
    assert initial_float >= 0

    # Initial must not be more precise than CCY allows (via dps)
    assert -Decimal(ccy.initial).normalize().as_tuple().exponent <= ccy.dps

def test_ccy_usd():
    usd = CCY.USD
    assert usd.name == "USD"
    assert usd.dps == 2
    assert usd.q == Decimal("1.00")
    assert usd.symbol == "$"

def test_ccy_from_string_valid():
    usd_strings = ["USD", "Usd", "usd", " USD", "  Usd ", "  usd   "]
    for s in usd_strings:
        assert CCY.from_string(s) == CCY.USD

def test_ccy_from_string_invalid():
    usd_strings = ["us d", "dollar", "U.S.D", "MUR", "$", "", " ", "0"]
    for s in usd_strings:
        assert CCY.from_string(s) is None

def test_currency_usd_creation_valid():
    quantities = ["0.00", "1.00", "2.20", "3.33", "4.04", "12345.00"]
    for q in quantities:
        try:
            Currency(CCY.USD, Decimal(q))
        except ValueError:
            assert False, f"Currency quantity ({q}) is invalid when it shouldn't have been"

def test_currency_usd_creation_invalid():
    quantities = ["0", "0.0", "0.000", "1", "1.1", "1.111", "123456"]
    for q in quantities:
        try:
            Currency(CCY.USD, Decimal())
            assert False, f"Currency quantity ({q}) is valid when it shouldn't have been"
        except ValueError:
            assert True

def test_currency_usd_creation_from_string_valid():
    quantities = ["0.00", "1.00", "2.20", "3.33", "4.04", "12345.00"]
    for q in quantities:
        try:
            Currency.from_string(CCY.USD, q)
        except ValueError:
            assert False, f"Currency quantity ({q}) is invalid when it shouldn't have been"

def test_currency_usd_creation_from_string_invalid():
    quantities = ["", " ", "!", "$", "a"]
    for q in quantities:
        try:
            Currency.from_string(CCY.USD, q)
            assert False, f"Currency quantity ({q}) is valid when it shouldn't have been"
        except Exception:
            assert True
