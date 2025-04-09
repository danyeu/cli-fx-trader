import re
from getpass import getpass
from typing import Callable, Optional

from fx_trader.currency import *
from fx_trader.db import *
from fx_trader.security import hash_password
from fx_trader.fx import *
from fx_trader.user import user
from fx_trader.transaction import Transaction


def print_lines(title: str = None, initial_newline: bool = True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if initial_newline:
                print()
            if title:
                print(f">>> {title}")
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def main_menu():
    while True:
        login_marker = "" if not user.exists() else f"[{user.username}]"

        if not user.exists():
            menu_options = [
                MenuOption("1", "Login", login),
                MenuOption("2", "New User", new_user),
            ]
        else:
            menu_options = [
                MenuOption("1", "Show portfolio", show_portfolio),
                MenuOption("2", "Show rates", show_rates),
                MenuOption("3", "Buy FX", buy_fx),
                MenuOption("4", "Sell FX", sell_fx),
                MenuOption("5", "Logout", logout)
            ]
        menu_options.append(MenuOption("x", "Exit", close))
        menu = Menu(menu_options)

        print()
        print(f">>> Main Menu {login_marker}")
        menu.run()

@print_lines("Create New User")
def new_user() -> None:
    print("Enter username and password. Enter blank value to cancel.")
    while True:
        new_username = input("Username: ").strip().lower()
        if len(new_username) == 0:
            print("Aborting: Blank username.")
            return
        if user_exists(new_username):
            print("User already exists.")
            continue
        break
    while True:
        new_password = getpass("Password: ")
        if len(new_password) == 0:
            print("Aborting: Blank password.")
            return
        new_password2 = getpass("Confirm password: ")
        if new_password != new_password2:
            print("Passwords do not match. Try again.")
            continue
        break
    hashed_password = hash_password(new_password)
    try:
        create_user(new_username, hashed_password)
        print(f"User {new_username} created!")
    except Exception:
        print("Error creating user.")

@print_lines("Login")
def login():
    print("Enter username and password. Enter blank value to cancel.")
    while True:
        username = input("Username: ").strip().lower()
        if len(username) == 0:
            print("Aborting: Blank username.")
            return
        password = getpass("Password: ")
        try:
            if not check_password(username, password):
                print("User or password incorrect.")
                continue
        except Exception:
            print("Error logging in.")
            return
        break

    user.set(get_user_id(username), username)
    print(f"Logged in as {username}")

@print_lines()
def logout():
    print(f"Logged out of {user.username}")
    user.logout()

@print_lines()
def close():
    print("Goodbye!")
    exit()

def print_args(*args: str):
    print("".join(args))

@print_lines()
def show_portfolio():
    df = get_portfolio(user.username)
    print(df.to_string(index=False, header=["Currency", "Quantity"]))

@print_lines("Show Rates")
def show_rates():
    try:
        rates = get_rates()
        print("1 USD =")
        for rate in rates:
            print(f"  {rate} {rates[rate]}")
    except Exception:
        print("Error getting FX rates.")

@print_lines("Buy FX")
def buy_fx():
    print("Enter FX to buy. Enter blank value to cancel.")
    print(", ".join(FX_CURRENCY_NAMES))
    # Verify FX
    while True:
        fx_ccy = input("FX to buy: ").strip().upper()
        if len(fx_ccy) == 0:
            print("Aborting: Blank currency.")
            return
        if fx_ccy not in FX_CURRENCY_NAMES:
            print("Invalid currency. Try again.")
            continue
        break
    fx_ccy = CCY.from_string(fx_ccy)
    base = get_currency_owned(BASE_CURRENCY)
    print(f"Balance: {BASE_CURRENCY.name} {base.quantity_str}")
    if base.quantity <= 0:
        print("Insufficient funds.")
        return

    # Verify quantity of base to spend
    while True:
        base_quantity_sold_str = input(f"Quantity to spend: {BASE_CURRENCY.name} ").strip()
        if len(base_quantity_sold_str) == 0:
            print("Aborting: Blank quantity.")
            return
        if not valid_quantity_sold(base_quantity_sold_str, BASE_CURRENCY):
            print("Invalid quantity. Try again.")
            continue
        base_sold = Currency.from_string(BASE_CURRENCY, base_quantity_sold_str)
        if base_sold.quantity > base.quantity:
            print("Insufficient funds. Try again.")
            continue
        break

    # Verify trade
    while True:
        if (fx_rate := get_rate(fx_ccy)) is None:
            print("Error getting FX rates.")
            return

        fx_bought = base_sold.to_fx(fx_ccy, fx_rate)
        transaction = Transaction(fx_bought, base_sold, fx_rate)
        print("Quote valid for 10 seconds:")
        print(transaction)
        while True:
            confirm = input("Confirm (y/n): ").strip().lower()
            if confirm == "n":
                print("Trade aborted.")
                return
            elif confirm == "y":
                if transaction.execute():
                    print("Confirmed!")
                    return
                print("Error executing transaction.")
                return

@print_lines("Sell FX")
def sell_fx():
    print("Enter FX to sell. Enter blank value to cancel.")
    print(", ".join(FX_CURRENCY_NAMES))
    # Verify FX
    while True:
        fx_ccy = input("FX to sell: ").strip().upper()
        if len(fx_ccy) == 0:
            print("Aborting: Blank currency.")
            return
        if fx_ccy not in FX_CURRENCY_NAMES:
            print("Invalid currency. Try again.")
            continue
        break
    fx_ccy = CCY.from_string(fx_ccy)
    fx = get_currency_owned(fx_ccy)
    print(f"Balance: {fx_ccy.name} {fx.quantity_str}")
    if fx.quantity <= 0:
        print("Insufficient funds.")
        return

    # Verify quantity of fx to sell
    while True:
        fx_quantity_sold_str = input(f"Quantity to sell: {fx_ccy.name} ").strip()
        if len(fx_quantity_sold_str) == 0:
            print("Aborting: Blank quantity.")
            return
        if not valid_quantity_sold(fx_quantity_sold_str, fx_ccy):
            print("Invalid quantity. Try again.")
            continue
        fx_sold = Currency.from_string(fx_ccy, fx_quantity_sold_str)
        if fx_sold.quantity > fx.quantity:
            print("Insufficient funds. Try again.")
            continue
        break

    # Verify trade
    while True:
        if (fx_rate := get_rate(fx_ccy)) is None:
            print("Error getting FX rates.")
            return

        base_bought = fx_sold.to_base(fx_rate)
        transaction = Transaction(base_bought, fx_sold, fx_rate)
        print("Quote valid for 10 seconds:")
        print(transaction)
        while True:
            confirm = input("Confirm (y/n): ").strip().lower()
            if confirm == "n":
                print("Trade aborted.")
                return
            elif confirm == "y":
                if transaction.execute():
                    print("Confirmed!")
                    return
                print("Error executing transaction.")
                return

class MenuOption:
    def __init__(self, selector: str, description: str, function: Callable):
        selector = selector.strip().lower()
        if len(selector) != 1:
            raise ValueError(f"Selector must be one character long: {selector}")
        if not selector.isalnum():
            raise ValueError(f"Selector must be alphanumeric: {selector}")

        description = description.strip()
        if len(selector) == 0:
            raise ValueError("Description must not be empty")

        self.selector = selector
        self.description = description
        self.function = function

    def execute(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def print(self) -> None:
        print(f"{self.selector}. {self.description}")

    def __str__(self) -> str:
        return "MenuOption(selector={}, description=\"{}\", function={})"\
            .format(self.selector, self.description, self.function.__name__)


class Menu:
    def __init__(self, options: Optional[list[MenuOption]] = []):
        self.options = []
        for option in options:
            self.add(option)

    def select(self, selector: str, *args, **kwargs):
        for option in self.options:
            if selector == option.selector:
                option.execute(*args, **kwargs)

    def add(self, option: MenuOption):
        # Ensure no duplicate selectors
        if option.selector in [o.selector for o in self.options]:
            raise ValueError(f"Selector already in menu options: {option.selector}")
        self.options.append(option)

    def print(self):
        for option in self.options:
            option.print()

    def run(self):
        self.print()
        while True:
            user_selection = input("   > ").strip().lower()
            try:
                self.select(user_selection)
                return
            except ValueError:
                continue
