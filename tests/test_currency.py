import pytest
from unittest.mock import MagicMock
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

def test_ccy_from_string():
    usd_strings = ["USD", "Usd", "usd", " USD", "  Usd ", "  usd   "]
    for s in usd_strings:
        assert CCY.from_string(s) == CCY.USD

def test_ccy_from_string_invalid():
    usd_strings = ["us d", "dollar", "U.S.D", "MUR", "$", "", " ", "0"]
    for s in usd_strings:
        assert CCY.from_string(s) is None

def test_currency_usd_creation():
    quantities = ["0.00", "1.00", "2.20", "3.33", "4.04", "12345.00"]
    for q in quantities:
        try:
            Currency(CCY.USD, Decimal(q))
        except ValueError:
            assert False, f"Currency quantity ({q}) is invalid when it shouldn't have been"

def test_currency_usd_creation_invalid():
    quantities = ["0", "0.0", "0.000", "1", "1.1", "1.111", "12345"]
    for q in quantities:
        try:
            Currency(CCY.USD, Decimal())
            assert False, f"Currency quantity ({q}) is valid when it shouldn't have been"
        except ValueError:
            assert True

def test_currency_usd_creation_from_string():
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

# === Currency: to_base ===
def test_currency_to_base():
    assert BASE_CURRENCY.dps == 2 # test assumption
    mock_ccy = MagicMock()
    mock_ccy.dps = 2
    mock_ccy.q = Decimal("1.00")

    # should round down, not up to 23.81
    fx = Currency(mock_ccy, Decimal("100.00"))
    base = fx.to_base(Decimal("4.2"))
    assert base.ccy == BASE_CURRENCY
    assert base.quantity == Decimal("23.80")

# === Currency: to_fx ===
def test_currency_to_fx():
    assert BASE_CURRENCY.dps == 2 # test assumption
    base = Currency(BASE_CURRENCY, Decimal("1.00"))
    mock_ccy = MagicMock()

    # should round down, not up to 1
    mock_ccy.dps = 2
    mock_ccy.q = Decimal("1.00")
    fx = base.to_fx(mock_ccy, Decimal("0.9999"))
    assert fx.ccy == mock_ccy
    assert fx.quantity == Decimal("0.99")

    # should round down, not up to 1
    mock_ccy.dps = 3
    mock_ccy.q = Decimal("1.000")
    fx = base.to_fx(mock_ccy, Decimal("0.9999"))
    assert fx.ccy == mock_ccy
    assert fx.quantity == Decimal("0.999")

# === valid_quantity_sold ===
def test_valid_quantity_sold_zero():
    # zero should be an invalid amount to sell
    n = 5
    quantities = []
    for i in range(1, n + 1):
        quantities.append("0" * i)
        for j in range(1, n + 1):
            quantities.append(f"{"0" * i}.{"0" * j}")
    print(quantities)
    for dps in range(n + 1):
        mock_ccy = MagicMock
        mock_ccy.dps = dps
        for q in quantities:
            assert not valid_quantity_sold(mock_ccy, q)

def test_valid_quantity_sold_invalid_dps():
    # tests that quantity more precise than CCY dps is invalid
    for dps in range(6):
        mock_ccy = MagicMock()
        mock_ccy.dps = dps
        quantity = f"1.{"1" * (dps + 1)}"
        assert not valid_quantity_sold(mock_ccy, quantity)

def test_valid_quantity_sold_invalid():
    quantities = ["", " ", "abc", "-1", "-12345"]
    for dps in range(6):
        mock_ccy = MagicMock()
        mock_ccy.dps = dps
        for q in quantities:
            assert not valid_quantity_sold(mock_ccy, q)

def test_valid_quantity_sold():
    for dps in range(6):
        mock_ccy = MagicMock()
        mock_ccy.dps = dps
        quantities = ["12345", "1"] + [f"1.{"1" * i}" for i in range(1, dps + 1)]
        for q in quantities:
            assert valid_quantity_sold(mock_ccy, q)
