# Учебные задания по ООП и ETL

Репозиторий объединяет три практических задания на Python: управление задачами проекта, модели лида и воронки продаж, а также ETL-систему обработки продаж интернет-магазина.

## Структура проекта

| Раздел | Файлы | Содержание |
|---|---|---|
| Управление задачами | `task_management.py`, `test_task_management.py` | Классы `Task`, `Project`, `Analysis`, `EnhancedAnalysis` |
| Лиды и воронка | `lead_funnel.py`, `test_lead_funnel.py` | Классы `Lead`, `Simulator`, `SalesFunnel`, интеграция с CRM через mock-тесты |
| ETL продаж | `sales_etl.py`, `test_sales_etl.py` | Извлечение из CSV, фильтрация, загрузка и аналитика продаж |
| Псевдокод и блок-схемы | `docs/` | Алгоритмы и Mermaid-блок-схемы для всех заданий |

## Запуск

Для запуска скриптов используется Python 3.10 или новее. Для CRM-задания требуется библиотека `requests`:

```bash
pip install requests
```

Демонстрационные сценарии:

```bash
python task_management.py
python lead_funnel.py
python sales_etl.py
```

Перед запуском `sales_etl.py` положите файл `sales.csv` в корень проекта. Пример входных данных находится в `sample_sales.csv`.

## Тестирование

Тесты можно запустить отдельными командами:

```bash
python test_task_management.py
python test_lead_funnel.py
python test_sales_etl.py
```

CRM-запросы в `test_lead_funnel.py` заменяются mock-объектами, поэтому тестирование не отправляет реальные данные во внешний сервис.

## Основные решения

В проекте используются инкапсуляция атрибутов, геттеры и сеттеры, статические методы анализа, итераторы, наследование, валидация входных данных и обработка ошибок. Для повторяющихся идентификаторов задач и этапов воронки предусмотрены исключения `ValueError`.

## Документация

Подробные инструкции находятся в `docs/README_sales_etl.md` и `docs/README_lead_funnel.md`. Псевдокод и блок-схемы доступны в файлах `docs/pseudocode_task_project.md`, `docs/pseudocode_lead_funnel.md` и `docs/pseudocode_sales_etl.md`.
