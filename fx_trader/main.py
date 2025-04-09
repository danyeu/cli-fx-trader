import os
from fx_trader import menu
from fx_trader.logger import LOGGER
from fx_trader.db import initialise_db

def setup():
    if os.getenv("OER_API_KEY") is None:
        LOGGER.error("No API key.", print_msg=True)
        os._exit(1)

    if not initialise_db():
        LOGGER.error("Failed to initialise database.", print_msg=True)
        os._exit(1)

def main():
    setup()
    print("Welcome to fx-trader!")
    menu.main_menu()

if __name__ == "__main__":
    main()
