import sqlite3
import pandas as pd

from utils.logger import LOGGER
from utils.security import verify_password
from utils.currency import Currency, CCY
from utils.user import user

DB_NAME = "fx_trader.db"

class DatabaseError(Exception):
    pass

def initialise_db() -> bool:
    try:
        # Connects to database (creates it if it doesn't exist)
        connection = sqlite3.connect(DB_NAME)

        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hash TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            currency TEXT NOT NULL,
            quantity TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        connection.commit()
    except sqlite3.DatabaseError as e:
        LOGGER.info("Database error when initialising database: %s", e)
        return False
    finally:
        if connection:
            connection.close()

    return True

def get_user_id(username: str) -> int:
    try:
        with sqlite3.connect(DB_NAME) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username, ))
            result = cursor.fetchone()
    except sqlite3.DatabaseError as e:
        LOGGER.info("Database error when searching user id: %s", username)
        raise e
    finally:
        if connection:
            connection.close()
    if result is None:
        LOGGER.info("No such username: %s", username)
        return None

    return int(result[0])

def user_exists(username: str) -> bool:
    try:
        with sqlite3.connect(DB_NAME) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username, ))
            result = cursor.fetchone()
    except sqlite3.DatabaseError as e:
        LOGGER.info("Database error when creating new user: %s", e)
        raise DatabaseError("Error checking if user exists.") from e
    finally:
        if connection:
            connection.close()

    return result is not None

def create_user(username: str, hashed_password: str):
    """Attempts to create new user"""
    try:
        if user_exists(username):
            LOGGER.info("Username already exists: %s", username)
    except Exception as e:
        raise DatabaseError("Error creating new user. User already exists.") from e

    try:
        with sqlite3.connect(DB_NAME) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                           (username, hashed_password))
            user_id = cursor.lastrowid
            for currency in CCY:
                cursor.execute("INSERT INTO portfolio (user_id, currency, quantity) VALUES (?, ?, ?)", (user_id, currency.name, currency.initial))
            connection.commit()
    except sqlite3.DatabaseError as e:
        LOGGER.info("Database error when creating new user portfolio: %s", e)
        raise DatabaseError("Error creating new user or checking password.") from e
    finally:
        if connection:
            connection.close()

def check_password(username: str, password: str) -> bool:
    try:
        with sqlite3.connect(DB_NAME) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT hash FROM users WHERE username = ?", (username, ))
            result = cursor.fetchone()
            if result is None:
                return False
            actual_hashed_password = result[0]
    except sqlite3.DatabaseError as e:
        LOGGER.info("Database error when checking password: %s", e)
        raise DatabaseError("Error creating new user or checking password.") from e
    finally:
        if connection:
            connection.close()
    return verify_password(password, actual_hashed_password)

def get_portfolio(username: str) -> pd.DataFrame:
    try:
        with sqlite3.connect(DB_NAME) as connection:
            query = """SELECT p.currency, p.quantity
                FROM users u JOIN portfolio p ON u.id = p.user_id
                WHERE u.username = ?"""
            df = pd.read_sql_query(query, connection, params=(username,))
            return df
    except Exception as e:
        LOGGER.info("Database error when getting portfolio: %s", e)
        raise DatabaseError("Error getting portfolio.") from e
    finally:
        if connection:
            connection.close()

def get_currency_owned(ccy: CCY) -> Currency:
    try:
        with sqlite3.connect(DB_NAME) as connection:
            cursor = connection.cursor()
            cursor.execute("""SELECT quantity FROM portfolio
                WHERE user_id = ? AND currency = ?""", (user.id, ccy.name))
            result = cursor.fetchone()
            quantity_str = result[0]
            return Currency.from_string(ccy, quantity_str)
    except Exception as e:
        LOGGER.info("Database error when getting quantity %s owned by user %s: %s",
                    ccy.name, user.username, e)
        raise DatabaseError("Error getting quantity owned.") from e
    finally:
        if connection:
            connection.close()

def update_currencies(currency1: CCY, quantity1: str, currency2: CCY, quantity2: str) -> bool:
    try:
        with sqlite3.connect(DB_NAME) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE portfolio SET quantity = ? WHERE user_id = ? and currency = ?",
                           (quantity1, user.id, currency1.name))
            cursor.execute("UPDATE portfolio SET quantity = ? WHERE user_id = ? and currency = ?",
                           (quantity2, user.id, currency2.name))
            connection.commit()
            return True
    except Exception:
        LOGGER.error("Database error when getting updating transaction...TODO", exc_info=True)
        return False
    finally:
        if connection:
            connection.close()
