import math
from typing import Any, Dict, List


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Считает сумму, которую удастся отложить в «Инвесткопилку» за месяц.

    :param month: месяц в формате "YYYY-MM"
    :param transactions: список транзакций с ключами
        "Дата операции" (строка "YYYY-MM-DD") и "Сумма операции" (число)
    :param limit: шаг округления (10, 50 или 100)
    :return: отложенная сумма
    """
    if limit <= 0:
        raise ValueError("Шаг округления должен быть положительным числом")

    total_saved = 0.0
    for transaction in transactions:
        if not transaction["Дата операции"].startswith(month):
            continue
        amount = transaction["Сумма операции"]
        if amount >= 0:  # копятся только траты
            continue
        spend = abs(amount)
        rounded = math.ceil(spend / limit) * limit
        total_saved += rounded - spend
    return round(total_saved, 2)


# if __name__ == "__main__":
#     import json
#     from pathlib import Path
#
#     BASE_DIR = Path(__file__).resolve().parent.parent
#     DATA_FILE = BASE_DIR / "data" / "transactions.json"
#     with open(DATA_FILE, "r", encoding="utf-8") as f:
#         transactions = json.load(f)["transactions"]
#
#     print(investment_bank("2026-05", transactions, 10))
