import json
from datetime import datetime
from pathlib import Path

from pandas import to_datetime

from src.utils import get_currency_rate, get_stock_prices, reader_xlsx_xls


def main_screen_by_site(date_str: str) -> str:
    if date_str == "":
        raise ValueError("Нельзя вводить пустоту. Введите дату: Y-m-d H:M:S")
    if date_str.isspace():
        raise ValueError("Ошибка ввода. Введите дату: Y-m-d H:M:S")
    df = reader_xlsx_xls("operations.xlsx")  # из модуля utils...
    df["Дата операции"] = to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    month = df[df["Дата операции"].between(month_start, date)]

    # читает данные из user_settings.json
    root_path = Path(__file__).resolve().parent.parent
    user_sett_pth = root_path / "user_settings.json"
    with open(user_sett_pth, "r") as f:
        user_sett = json.load(f)

    # приветствие по времени из входной строки
    if date.hour < 6:
        greeting = "Доброй ночи"
    elif date.hour < 12:
        greeting = "Доброе утро"
    elif date.hour < 18:
        greeting = "Добрый день"
    else:
        greeting = "Добрый вечер"

    # расходы по картам
    spend = month[month["Сумма операции"] < 0]
    # noinspection PyUnresolvedReferences
    cards = spend.groupby("Номер карты")["Сумма операции"].sum().abs().round(2)
    cards_list = [
        {"last_digits": str(card)[1:], "total_spent": float(total), "cashback": round(float(total) / 100, 2)}
        for card, total in cards.items()
    ]

    # топ-5 по сумме платежа
    top5 = month.reindex(month["Сумма платежа"].abs().sort_values(ascending=False).index).head(5)
    top_list = [
        {
            "date": row["Дата платежа"],
            "amount": float(row["Сумма платежа"]),
            "category": row["Категория"],
            "description": row["Описание"],
        }
        for _, row in top5.iterrows()
    ]

    result = {
        "greeting": greeting,
        "cards": cards_list,
        "top_transactions": top_list,
        "currency_rates": [get_currency_rate(cur) for cur in user_sett["user_currencies"]],  # из модуля utils...
        "stock_prices": get_stock_prices(user_sett.get("user_stocks")),
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


# if __name__ == "__main__":
#
#     result = main_screen_by_site("2020-12-29 19:20:00")  # 2020-12-29 19:20:00
#     print(result)
