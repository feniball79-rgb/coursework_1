from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests
import yfinance as yf
from pandas import DataFrame, to_datetime

# Приказывает печатать DataFrame развёрнутыми таблицами - глобально.
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 100)

# путь в корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent


def reader_xlsx_xls(filename: str) -> DataFrame:

    # путь к читаемому файлу .xlsx
    DATA_FILE = BASE_DIR / "data" / filename

    #  Проверка расширения
    if DATA_FILE.suffix.lower() not in (".xlsx", ".xls"):
        raise ValueError(f"Ожидается Excel-файл (.xlsx или .xls), но передано: {filename}")

    return pd.read_excel(DATA_FILE)  # .to_dict(orient="records") # перевод в json - моя шпаргалка


# if __name__ == "__main__":
#
#     res = reader_xlsx_xls("operations.xlsx")
# print(res.head())


# def greeting() -> str:
#     """Приветствие пользователя, относительно времени суток."""
#
#     time_now = datetime.now().hour
#
#     if time_now in range(0, 6):
#         printing = "Доброй ночи"
#     elif time_now in range(6, 12):
#         printing = "Доброе утро"
#     elif time_now in range(12, 18):
#         printing = "Добрый день"
#     else:
#         printing = "Добрый вечер"
#
#     return printing


# if __name__ == "__main__":
#
#     res = greeting()
#     # print(res)


def process_data(date_start: str, date_end: str) -> DataFrame:
    """Фильтрует DF по заданному диапазону дат и переводит из str в datetime формат."""

    start = datetime.strptime(date_start, "%d.%m.%Y")
    end = datetime.strptime(date_end, "%d.%m.%Y")

    # читаем функцией reader_xlsx_xls, написанной выше.
    data = reader_xlsx_xls("operations.xlsx")
    data["Дата операции"] = to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    mask = data["Дата операции"].between(start, end)
    return data[mask]


# if __name__ == "__main__":
#
#     res = process_data("02.01.2019", "31.01.2020")
#     print(res)


def get_currency_rate(currency_code: str) -> Dict[str, Any] | str:
    """
    Получает курс валюты на текущую дату из API ЦБ РФ и возвращает его в формате JSON.
    :param currency_code:
    :return: JSON
    """
    if currency_code != "":
        url = f"https://www.cbr-xml-daily.ru//daily_json.js"
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to get currency rate")
        data = response.json()
        currency_data = data["Valute"].get(currency_code.upper())
        if not currency_data:
            raise ValueError(f"No data for currency {currency_code}")
        return {
            "currency": currency_code,
            "rate": round(currency_data["Value"], 2),
        }
    else:
        return "ValueError: No data for currency"


# if __name__ == "__main__":
#
#     res = get_currency_rate("eur")
#     # print(res)


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """Текущие цены акций в формате [{"stock": "AAPL", "price": 150.12}]"""
    prices = []
    for symbol in stocks:
        try:
            hist = yf.Ticker(symbol).history(period="1d")
        except Exception:
            continue
        if hist.empty:
            continue
        prices.append(
            {
                "stock": symbol.upper(),
                "price": round(float(hist.iloc[-1]["Close"]), 2),
            }
        )
    return prices


# if __name__ == "__main__":
#     x = get_stock_prices(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
#     print(x)
