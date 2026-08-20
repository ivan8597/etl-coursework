from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional


class Sale:
    """Объект одной продажи."""

    def __init__(self, sale_id: int | str, sale_date: date | str, amount: float | str, product: str):
        self.set_id(sale_id)
        self.set_date(sale_date)
        self.set_amount(amount)
        self.set_product(product)

    @staticmethod
    def _parse_date(value: date | str) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            value = value.strip()
            for date_format in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
                try:
                    return datetime.strptime(value, date_format).date()
                except ValueError:
                    continue
        raise ValueError(f"Некорректная дата: {value!r}")

    def get_id(self) -> int | str:
        return self.__id

    def set_id(self, value: int | str) -> None:
        if value is None or str(value).strip() == "":
            raise ValueError("Идентификатор продажи не может быть пустым")
        try:
            self.__id = int(value)
        except (TypeError, ValueError):
            self.__id = str(value).strip()

    def get_date(self) -> date:
        return self.__date

    def set_date(self, value: date | str) -> None:
        self.__date = self._parse_date(value)

    def get_amount(self) -> float:
        return self.__amount

    def set_amount(self, value: float | str) -> None:
        if isinstance(value, str):
            value = value.strip().replace(" ", "").replace(",", ".")
        amount = float(value)
        if amount < 0:
            raise ValueError("Сумма продажи не может быть отрицательной")
        self.__amount = amount

    def get_product(self) -> str:
        return self.__product

    def set_product(self, value: str) -> None:
        if value is None or str(value).strip() == "":
            raise ValueError("Название товара не может быть пустым")
        self.__product = str(value).strip()

    # Удобный интерфейс через свойства, сохраняя требуемые геттеры и сеттеры.
    id = property(get_id, set_id)
    date = property(get_date, set_date)
    amount = property(get_amount, set_amount)
    product = property(get_product, set_product)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.get_id(),
            "date": self.get_date().isoformat(),
            "amount": f"{self.get_amount():.2f}",
            "product": self.get_product(),
        }

    def __repr__(self) -> str:
        return (
            f"Sale(id={self.get_id()!r}, date={self.get_date().isoformat()!r}, "
            f"amount={self.get_amount()!r}, product={self.get_product()!r})"
        )


class Extraction:
    """Слой извлечения данных. Новые источники можно добавлять отдельными методами."""

    @staticmethod
    def from_csv(file_path: str | Path) -> list[Sale]:
        required_columns = {"id", "date", "amount", "product"}
        sales: list[Sale] = []

        with Path(file_path).open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                raise ValueError("CSV-файл не содержит заголовок")

            actual_columns = {column.strip().lower() for column in reader.fieldnames}
            missing = required_columns - actual_columns
            if missing:
                raise ValueError(f"В CSV отсутствуют обязательные столбцы: {sorted(missing)}")

            for row_number, row in enumerate(reader, start=2):
                try:
                    normalized = {
                        (key.strip().lower() if key else ""): (value or "").strip()
                        for key, value in row.items()
                    }
                    sales.append(
                        Sale(
                            sale_id=normalized["id"],
                            sale_date=normalized["date"],
                            amount=normalized["amount"],
                            product=normalized["product"],
                        )
                    )
                except (KeyError, TypeError, ValueError) as error:
                    raise ValueError(f"Ошибка в строке CSV №{row_number}: {error}") from error

        return sales


class Transformation:
    """Слой преобразования и фильтрации продаж."""

    @staticmethod
    def filter_by_date(
        sales_data: Iterable[Sale],
        start_date: date | str,
        end_date: date | str,
    ) -> list[Sale]:
        start = Sale._parse_date(start_date)
        end = Sale._parse_date(end_date)
        if start > end:
            raise ValueError("start_date не может быть позже end_date")
        return [sale for sale in sales_data if start <= sale.get_date() <= end]

    @staticmethod
    def filter_by_amount(
        sales_data: Iterable[Sale],
        min_amount: float,
        max_amount: float,
    ) -> list[Sale]:
        minimum = float(min_amount)
        maximum = float(max_amount)
        if minimum > maximum:
            raise ValueError("min_amount не может быть больше max_amount")
        return [sale for sale in sales_data if minimum <= sale.get_amount() <= maximum]


class Loading:
    """Слой загрузки обработанных продаж в CSV-файл."""

    @staticmethod
    def to_csv(sales_data: Iterable[Sale], file_path: str | Path) -> None:
        with Path(file_path).open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["id", "date", "amount", "product"])
            writer.writeheader()
            for sale in sales_data:
                writer.writerow(sale.to_dict())


class Analysis(Loading):
    """Аналитика продаж; класс расширяет Loading, как указано в задании."""

    @staticmethod
    def calculate_total_sales(sales_data: Iterable[Sale]) -> float:
        return round(sum(sale.get_amount() for sale in sales_data), 2)

    @staticmethod
    def calculate_average_sales(sales_data: Iterable[Sale]) -> float:
        sales = list(sales_data)
        if not sales:
            return 0.00
        return round(Analysis.calculate_total_sales(sales) / len(sales), 2)


if __name__ == "__main__":
    input_file = "sales.csv"
    output_file = "filtered_sales.csv"

    sales = Extraction.from_csv(input_file)
    filtered_sales = Transformation.filter_by_date(sales, "2024-01-01", "2024-12-31")
    filtered_sales = Transformation.filter_by_amount(filtered_sales, 100, 10_000)

    Loading.to_csv(filtered_sales, output_file)
    print(f"Общая сумма: {Analysis.calculate_total_sales(filtered_sales):.2f}")
    print(f"Средняя сумма: {Analysis.calculate_average_sales(filtered_sales):.2f}")
    print(f"Сохранено продаж: {len(filtered_sales)}")
