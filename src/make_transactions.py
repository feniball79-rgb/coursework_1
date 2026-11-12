# """Генератор тестовых транзакций для «Инвесткопилки» (faker)."""
#
#
# import random
# from pathlib import Path
#
# from faker import Faker
#
# fake = Faker("ru_RU")
#
# BASE_DIR = Path(__file__).resolve().parent.parent
# OUTPUT_FILE = BASE_DIR / "data" / "transactions.json"
#
#
# def make_transactions(count: int = 50, seed: int | None = None) -> list[dict]:
#     """Возвращает список транзакций вида {"Дата операции": "YYYY-MM-DD", "Сумма операции": число}."""
#     rng = random.Random(seed)  # SeedStream deprecated; обычный Random надежнее
#     transactions = []
#     for _ in range(count):
#         transactions.append(
#             {
#                 "Дата операции": fake.date_between(start_date="-180d", end_date="today").isoformat(),
#                 "Сумма операции": round(rng.uniform(-20000, 5000), 2),
#             }
#         )
#     return transactions


# if __name__ == "__main__":
# import json
#
# OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
# data = {"transactions": make_transactions(50, seed=42)}
# with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)
# print(f"Записано {len(data['transactions'])} транзакций в {OUTPUT_FILE}")
