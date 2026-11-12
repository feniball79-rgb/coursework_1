import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def transactions():
    return pd.DataFrame(
        {
            "Дата операции": [
                "20.12.2021 12:00:00",
                "01.12.2021 10:00:00",
                "01.07.2021 10:00:00",  # старше трёх месяцев
                "20.12.2021 13:00:00",  # пополнение, не трата
            ],
            "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты", "Супермаркеты"],
            "Сумма операции": [-100.0, -50.0, -1000.0, 500.0],
        }
    )


def test_three_months_window(transactions):
    result = spending_by_category(transactions, "Супермаркеты", date="31.12.2021")
    assert len(result) == 2  # старые и пополнение отсечены


def test_other_category_empty(transactions):
    result = spending_by_category(transactions, "Фастфуд", date="31.12.2021")
    assert result.empty


def test_decorated_writes_file(transactions, tmp_path):
    # tmp_path — встроенная фикстура pytest: временная папка под тест
    from src.reports import report_to_file

    target = tmp_path / "out.json"

    @report_to_file(str(target))
    def report():
        return spending_by_category(transactions, "Супермаркеты", date="31.12.2021")

    report()
    content = target.read_text(encoding="utf-8")
    assert "Супермаркеты" in content
