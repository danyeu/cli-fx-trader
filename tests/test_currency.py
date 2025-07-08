from decimal import Decimal
from types import MethodType
import pytest

from fx_trader.utils.currency import CCY, BASE_CURRENCY, Currency

# === CCY: Attributes ===
@pytest.mark.parametrize("ccy", [c for c in CCY])
def test_dps(ccy):
    assert isinstance(ccy.dps, int)
    assert ccy.dps >= 0

@pytest.mark.parametrize("ccy", [c for c in CCY])
def test_q(ccy):
    assert isinstance(ccy.q, Decimal)
    assert ccy.dps >= 0

@pytest.mark.parametrize("ccy", [c for c in CCY])
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

# === CCY: USD ===
def test_ccy_usd():
    usd = CCY.USD
    assert usd.name == "USD"
    assert usd.dps == 2
    assert usd.q == Decimal("1.00")
    assert usd.symbol == "$"

# === CCY: from_string ===
@pytest.mark.parametrize("string", ["USD", "Usd", "usd", " USD", "  Usd ", "  usd   "])
def test_ccy_usd_from_string(string):
    assert CCY.from_string(string) == CCY.USD

@pytest.mark.parametrize("string", ["us d", "dollar", "U.S.D", "MUR", "$", "", " ", "0"])
def test_ccy_usd_from_string_invalid(string):
    assert CCY.from_string(string) is None

# === Currency ===
@pytest.mark.parametrize("quantity", ["0.00", "1.00", "2.20", "3.33", "4.04", "12345.00"])
def test_currency_usd_creation_valid(quantity):
    try:
        Currency(CCY.USD, Decimal(quantity))
    except ValueError:
        assert False, f"Currency quantity ({quantity}) is invalid when it shouldn't have been"

@pytest.mark.parametrize("quantity", ["0", "0.0", "0.000", "1", "1.1", "1.111", "12345"])
def test_currency_usd_creation_invalid( quantity):
    try:
        Currency(CCY.USD, Decimal(quantity))
        assert False, f"Currency quantity ({quantity}) is valid when it shouldn't have been"
    except ValueError:
        assert True

@pytest.mark.parametrize("quantity", ["0.0", "0.00", "0.000", "1.0", "1.1", "1.11", "1.111"])
def test_currency_jpy_creation_invalid(quantity):
    try:
        Currency(CCY.JPY, Decimal(quantity))
        assert False, f"Currency quantity ({quantity}) is valid when it shouldn't have been"
    except ValueError:
        assert True

# === Currency: from_string ===
@pytest.mark.parametrize("quantity", ["0.00", "1.00", "2.20", "3.33", "4.04", "12345.00"])
def test_currency_usd_creation_from_string(quantity):
    try:
        Currency.from_string(CCY.USD, quantity)
    except ValueError:
        assert False, f"Currency quantity ({quantity}) is invalid when it shouldn't have been"

@pytest.mark.parametrize("quantity", ["", " ", "!", "$", "a"])
def test_currency_usd_creation_from_string_invalid(quantity):
    try:
        Currency.from_string(CCY.USD, quantity)
        assert False, f"Currency quantity ({quantity}) is valid when it shouldn't have been"
    except Exception:
        assert True

# === Currency: to_base ===
def test_currency_to_base(mocker):
    assert BASE_CURRENCY.dps == 2 # test assumption
    mock_ccy = mocker.Mock()
    mock_ccy.dps = 2
    mock_ccy.q = Decimal("1.00")

    # should round down, not up to 23.81
    fx = Currency(mock_ccy, Decimal("100.00"))
    base = fx.to_base(Decimal("4.2"))
    assert base.ccy == BASE_CURRENCY
    assert base.quantity == Decimal("23.80")

# === Currency: to_fx ===
@pytest.mark.parametrize("dps,q,base_quantity,fx_rate,expected_fx_quantity", [
    (0, Decimal("1"), Decimal("5.55"), Decimal("0.66"), Decimal("3")),
    (1, Decimal("1.0"), Decimal("12.12"), Decimal("13.13"), Decimal("159.1")),
    (2, Decimal("1.00"), Decimal("50.00"), Decimal("0.1234"), Decimal("6.17")),
    (3, Decimal("1.000"), Decimal("123456.00"), Decimal("0.00001"), Decimal("1.234")),
    (4, Decimal("1.0000"), Decimal("10.00"), Decimal("1"), Decimal("10.0000")),
    (5, Decimal("1.00000"), Decimal("42.00"), Decimal("0.9999"), Decimal("41.9958"))])
def test_currency_to_fx(mocker, dps, q, base_quantity, fx_rate, expected_fx_quantity):
    """Tests that the conversion from base to FX rounds down correctly."""
    assert BASE_CURRENCY.dps == 2 # test assumption
    base = Currency(BASE_CURRENCY, base_quantity)
    mock_ccy = mocker.Mock()
    mock_ccy.dps = dps
    mock_ccy.q = q
    fx = base.to_fx(mock_ccy, fx_rate)
    assert fx.ccy == mock_ccy
    assert fx.quantity == expected_fx_quantity

@pytest.mark.parametrize("dps,q,base_quantity,fx_rate,expected_fx_quantity", [
    (0, Decimal("1"), Decimal("1.00"), Decimal("0.99999"), Decimal("0")),
    (1, Decimal("1.0"), Decimal("1.00"), Decimal("0.99999"), Decimal("0.9")),
    (2, Decimal("1.00"), Decimal("1.00"), Decimal("0.99999"), Decimal("0.99")),
    (3, Decimal("1.000"), Decimal("1.00"), Decimal("0.99999"), Decimal("0.999")),
    (4, Decimal("1.0000"), Decimal("1.00"), Decimal("0.99999"), Decimal("0.9999")),
    (5, Decimal("1.00000"), Decimal("1.00"), Decimal("0.99999"), Decimal("0.99999"))])
def test_currency_to_fx_rounddown(mocker, dps, q, base_quantity, fx_rate, expected_fx_quantity):
    """Tests that the conversion from base to FX rounds down correctly."""
    assert BASE_CURRENCY.dps == 2 # test assumption
    base = Currency(BASE_CURRENCY, base_quantity)
    mock_ccy = mocker.Mock()
    mock_ccy.dps = dps
    mock_ccy.q = q
    fx = base.to_fx(mock_ccy, fx_rate)
    assert fx.ccy == mock_ccy
    assert fx.quantity == expected_fx_quantity

# === valid_quantity ===
@pytest.mark.parametrize("quantity", [
    "0", "0.0", "0.00", "0.000", "0.0000", "0.00000",
    "00", "00.0", "00.00", "00.000", "00.0000", "00.00000",
    "000", "000.0", "000.00", "000.000", "000.0000", "000.00000",
    "0000", "0000.0", "0000.00", "0000.000", "0000.0000", "0000.00000",
    "00000", "00000.0", "00000.00", "00000.000", "00000.0000", "00000.00000"])
def test_valid_quantity_zero(mocker, quantity):
    """Tests that zero is an invalid quantity to trade, regardless of CCY dps."""
    for dps in range(10):
        mock_ccy = mocker.Mock()
        mock_ccy.dps = dps
        mock_ccy.valid_quantity = MethodType(CCY.valid_quantity, mock_ccy)
        assert not mock_ccy.valid_quantity(quantity)

@pytest.mark.parametrize("dps, quantity", [
    (0, "1.1"), (0, "1.11"),
    (1, "1.11"), (1, "1.111"),
    (2, "1.111"), (2, "1.1111"),
    (3, "1.1111"), (3, "1.11111"),
    (4, "1.11111"), (4, "1.111111"),
    (5, "1.111111"), (5, "1.1111111")])
def test_valid_quantity_invalid_dps(mocker, dps, quantity):
    """Tests that quantities more precise than the CCY dps are invalid."""
    mock_ccy = mocker.Mock()
    mock_ccy.dps = dps
    mock_ccy.valid_quantity = MethodType(CCY.valid_quantity, mock_ccy)
    assert not mock_ccy.valid_quantity(quantity)

@pytest.mark.parametrize("quantity", ["", " ", "abc", "-1", "-12345"])
def test_valid_quantity_invalid(mocker, quantity):
    """Tests that invalid quantities are rejected regardless of CCY dps."""
    mock_ccy = mocker.Mock()
    for dps in range(10):
        mock_ccy.dps = dps
        mock_ccy.valid_quantity = MethodType(CCY.valid_quantity, mock_ccy)
        assert not mock_ccy.valid_quantity(quantity)

@pytest.mark.parametrize("dps, quantity", [
    (0, "1"), (0, "123"), (0, "1.0"), (0, "01.00"),
    (1, "1"), (1, "123"), (1, "1.1"), (1, "01.10"),
    (2, "1"), (2, "123"), (2, "1.11"), (2, "01.110"),
    (3, "1"), (3, "123"), (3, "1.111"), (3, "01.1110"),
    (4, "1"), (4, "123"), (4, "1.1111"), (4, "01.11110"),
    (5, "1"), (5, "123"), (5, "1.11111"), (5, "01.111110")])
def test_valid_quantity(mocker, dps, quantity):
    mock_ccy = mocker.Mock()
    mock_ccy.dps = dps
    mock_ccy.valid_quantity = MethodType(CCY.valid_quantity, mock_ccy)
    assert mock_ccy.valid_quantity(quantity)
