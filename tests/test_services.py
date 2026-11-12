import json
from pathlib import Path

import pytest

from src.services import investment_bank

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "transactions.json"


def load_transactions() -> list[dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["transactions"]


@pytest.mark.parametrize(
    "limit, expected",
    [
        (100, 123.23),
        (50, 73.23),
        (10, 13.23),
    ],
)
def test_october_2026(limit, expected):
    assert investment_bank("2026-10", load_transactions(), limit) == pytest.approx(expected)


def test_exact_multiple_gives_zero():
    """Трата ровно 1900 при limit=50 кратна — вклад ноль."""
    tx = [{"Дата операции": "2026-10-01", "Сумма операции": -1900}]
    assert investment_bank("2026-10", tx, 50) == 0


def test_positive_operations_ignored():
    """Пополнения не копятся: в мае 2026 есть +2304.49 и +735.12."""
    tx = [
        {"Дата операции": "2026-05-30", "Сумма операции": 2304.49},
        {"Дата операции": "2026-05-27", "Сумма операции": 735.12},
    ]
    assert investment_bank("2026-05", tx, 100) == 0


def test_month_without_transactions_returns_zero():
    assert investment_bank("2025-01", load_transactions(), 100) == 0


def test_invalid_limit_raises():
    with pytest.raises(ValueError):
        investment_bank("2026-10", load_transactions(), 0)


def test_spent_amount_is_not_inflated_by_incomes():
    """Сентябрь: 11 трат и 2 пополнения — пополнения не должны завысить результат."""
    result = investment_bank("2026-09", load_transactions(), 100)
    total_spent = sum(
        abs(t["Сумма операции"])
        for t in load_transactions()
        if t["Дата операции"].startswith("2026-09") and t["Сумма операции"] < 0
    )
    assert result < total_spent
    assert result > 0
