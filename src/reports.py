import json
import logging
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union
from venv import logger

import pandas as pd
from poetry.core.poetry import logger

F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger("reports")
logging.basicConfig(level=logging.INFO, format="%(asctime)s-%(levelname)s-%(message)s")
DEFAULT_REPORT_FILE = "report.json"


def _save_reports(data: Any, filename: str) -> None:
    """Записывает результат отчёта в json файл"""
    if isinstance(data, pd.DataFrame):
        data = data.where(pd.notna(data), None)
        data = data.to_dict(orient="records")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, default=str)
    logger.info(f"Отчёт сохранён в файл - {filename}")


def report_to_file(func_or_filename: Union[Callable[..., Any], str]) -> Callable[..., Any]:
    """
    Декоратор для функций-отчётов
    Без параметра: @report_to_file -> пишет в report.json
    С параметром: @report_to_file(my_report.json) -> в ваш файл
    """

    def make_wrapper(func: Callable[..., Any], filename: str) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            try:
                _save_reports(result, filename)
            except (OSError, TypeError) as e:
                logger.error(f"Не удалось сохранить отчёт в {filename}: {e}")
            return result

        return wrapper

    # Случай использования без скобок: декоратору сразу передали функцию
    if callable(func_or_filename):
        return make_wrapper(func_or_filename, DEFAULT_REPORT_FILE)

    # Случай с параметром: вернули «ожидание» имени файла
    filename = func_or_filename

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return make_wrapper(func, filename)

    return decorator


@report_to_file
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Траты по категории за последние три месяца от переданной даты.

    :param transactions: датафрейм с транзакциями
    :param category: название категории, например "Супермаркеты"
    :param date: опорная дата "DD.MM.YYYY"; если не задана — текущая дата
    :return: датафрейм с тратами за период
    """
    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

    end = pd.to_datetime(date, dayfirst=True) if date is not None else pd.Timestamp.now()
    start = end - pd.DateOffset(months=3)

    mask = (df["Категория"] == category) & (df["Сумма операции"] < 0) & (df["Дата операции"].between(start, end))

    result = df.loc[mask].sort_values("Дата операции")
    logger.info(f"Отчёт <<{category}>>: {len(result)} операций за {start:%Y-%m-%d} - {end:%Y-%m-%d}")

    return result


# if __name__ == "__main__":
#
#     from src.utils import reader_xlsx_xls
#
#     df = reader_xlsx_xls("operations.xlsx")
#     report = spending_by_category(df, "Супермаркеты", date="31.12.2021")
#     print(report.head(10))
