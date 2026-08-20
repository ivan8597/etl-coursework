from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from sales_etl import Analysis, Extraction, Loading, Transformation


PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_PATH = PROJECT_ROOT / "examples" / "sample_sales.csv"


sales = Extraction.from_csv(INPUT_PATH)
assert len(sales) == 4
assert sales[0].get_product() == "Клавиатура"
assert sales[0].get_date() == date(2024, 1, 15)

by_date = Transformation.filter_by_date(sales, "2024-01-01", "2024-12-31")
assert len(by_date) == 3

by_amount = Transformation.filter_by_amount(by_date, 100, 1000)
assert len(by_amount) == 2
assert Analysis.calculate_total_sales(by_amount) == 1120.49
assert Analysis.calculate_average_sales(by_amount) == 560.25

with TemporaryDirectory() as temporary_directory:
    output_path = Path(temporary_directory) / "filtered_sales.csv"
    Loading.to_csv(by_amount, output_path)
    reloaded = Extraction.from_csv(output_path)
    assert len(reloaded) == 2
    assert reloaded[1].get_amount() == 999.99

print("Все проверки пройдены успешно.")
