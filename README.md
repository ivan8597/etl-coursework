# Python Coursework Collection

Единый публичный репозиторий со всеми выполненными учебными заданиями на Python: автопроверка кода, управление задачами, воронка продаж, ETL-обработка продаж и анализ пользовательских сессий.

## Содержание

| Раздел | Основные файлы | Назначение |
|---|---|---|
| Автогрейдер | `autograder.py`, `test_autograder.py` | AST-проверка, запуск решений, тайм-аут и сравнение с эталоном |
| Управление задачами | `task_management.py`, `test_task_management.py` | `Task`, `Project`, `Analysis`, `EnhancedAnalysis` |
| Воронка продаж | `lead_funnel.py`, `test_lead_funnel.py` | `Lead`, `Simulator`, `SalesFunnel` и mock-тестирование CRM |
| ETL продаж | `sales_etl.py`, `test_sales_etl.py` | Извлечение CSV, фильтрация, загрузка и аналитика |
| Анализ сессий | `session_analysis.py`, `sessions.csv` | JSON-сессии, конверсии, длительность и количество сессий |
| Псевдокод | `docs/`, `pseudocode_autograder.md` | Псевдокод и Mermaid-блок-схемы |

## Установка

Требуется Python 3.10 или новее. Для CRM-задания установите зависимость:

```bash
python -m pip install -r requirements.txt
```

## Запуск заданий

```bash
python task_management.py
python lead_funnel.py
python sales_etl.py
python session_analysis.py sessions.csv
```

Для ETL-примера входной файл `sales.csv` уже находится в корне репозитория. Обработанный результат `filtered_sales.csv` создаётся при запуске и не включается в Git.

## Автогрейдер

```bash
python autograder.py standard_solution.py user_solution.py tests.json --output output.txt
```

По умолчанию проверяется функция `solve`. Имя функции и лимит времени можно изменить через `--function` и `--timeout`. Проверка пользовательского кода через AST является учебным фильтром и не заменяет полноценную изоляцию недоверенного кода в промышленной системе.

## Анализ сессий

Скрипт `session_analysis.py` рассчитывает четыре значения:

```text
res  — среднее время от начала сессии до conversion;
res2 — среднюю продолжительность сессии;
res3 — среднее число сессий на активный пользовательский день;
res4 — среднее общее число сессий на пользователя.
```

Для файла из задания контрольные результаты составляют `467.24`, `901.35`, `1.11` и `5.28` соответственно.

## Тестирование

```bash
python test_autograder.py
python test_task_management.py
python test_lead_funnel.py
python test_sales_etl.py
```

Все тесты запускаются без Ubuntu-зависимых абсолютных путей. В тестах CRM используются mock-объекты, а временные результаты ETL и автогрейдера исключены через `.gitignore`.
