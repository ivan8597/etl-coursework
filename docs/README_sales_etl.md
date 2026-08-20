# ETL-система обработки продаж

Реализация выполнена на Python без внешних зависимостей. Основной файл — `sales_etl.py`.

## Формат входного CSV

Файл должен содержать столбцы `id`, `date`, `amount`, `product`:

```csv
id,date,amount,product
1,2024-01-15,120.50,Клавиатура
2,2024-02-10,2500,Монитор
```

Поддерживаются даты в форматах `YYYY-MM-DD`, `DD.MM.YYYY` и `DD/MM/YYYY`. Десятичный разделитель суммы может быть точкой или запятой.

## Основные классы

`Sale` хранит идентификатор, дату, сумму и название товара и предоставляет методы `get_*` и `set_*` для каждого атрибута.

`Extraction.from_csv(file_path)` извлекает строки CSV и возвращает список объектов `Sale`.

`Transformation.filter_by_date(sales_data, start_date, end_date)` выполняет включающую фильтрацию по датам. `Transformation.filter_by_amount(sales_data, min_amount, max_amount)` выполняет включающую фильтрацию по сумме.

`Loading.to_csv(sales_data, file_path)` сохраняет список продаж в CSV.

`Analysis.calculate_total_sales(sales_data)` возвращает общую сумму, а `Analysis.calculate_average_sales(sales_data)` — среднюю сумму продажи. Оба результата округляются до двух знаков после запятой. Для пустого списка средняя сумма равна `0.00`.

## Пример запуска

```python
from sales_etl import Analysis, Extraction, Loading, Transformation

sales = Extraction.from_csv("sales.csv")
sales = Transformation.filter_by_date(sales, "2024-01-01", "2024-12-31")
sales = Transformation.filter_by_amount(sales, 100, 10000)

Loading.to_csv(sales, "filtered_sales.csv")
print(Analysis.calculate_total_sales(sales))
print(Analysis.calculate_average_sales(sales))
```

Для запуска встроенного примера в самом модуле используйте файл `sales.csv` в текущей директории:

```bash
python3 sales_etl.py
```

Проверка реализации выполнена отдельным тестовым сценарием: извлечение, обе фильтрации, расчёт общей и средней суммы, сохранение и повторное чтение CSV проходят успешно.
