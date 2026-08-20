from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"created_at", "user_id", "problem_id", "is_correct", "type"}
ONE_HOUR = pd.Timedelta(hours=1)


def load_data(file_path: str | Path, sep: str = ";") -> pd.DataFrame:
    """Загружает выгрузку и приводит временную метку к datetime."""

    df = pd.read_csv(file_path, sep=sep)
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"В файле отсутствуют столбцы: {sorted(missing_columns)}")

    df["created_at"] = pd.to_datetime(df["created_at"], errors="raise")
    return df


def average_solution_time(df: pd.DataFrame) -> float:
    """Среднее время решения задачи в секундах.

    Для каждой пары пользователь–задача берётся интервал от первой попытки
    submit до первого правильного submit. Решения с первой попытки исключаются.
    Затем сначала считается среднее по каждой задаче, а потом среднее этих средних.
    """

    submit = df[df["type"].eq("submit")].copy()
    submit = submit.sort_values(["user_id", "problem_id", "created_at"])

    first_attempt = submit.groupby(["user_id", "problem_id"])["created_at"].min()
    first_correct = (
        submit[submit["is_correct"].eq(1)]
        .groupby(["user_id", "problem_id"])["created_at"]
        .min()
    )

    solution = pd.concat(
        [first_attempt.rename("first_attempt"), first_correct.rename("first_correct")],
        axis=1,
    ).dropna()

    # Исключаем пользователей, решивших задачу с первой попытки.
    solution = solution[solution["first_correct"] > solution["first_attempt"]].copy()
    if solution.empty:
        return 0.0

    solution["duration_seconds"] = (
        solution["first_correct"] - solution["first_attempt"]
    ).dt.total_seconds()

    mean_by_problem = solution.groupby(level="problem_id")["duration_seconds"].mean()
    return round(float(mean_by_problem.mean()), 2)


def average_daily_active_hours(df: pd.DataFrame) -> float:
    """Среднее число активных часов на пользователя за день.

    Перерывы длиннее одного часа не включаются в длительность активности.
    Расчёт ведётся отдельно для каждой пары пользователь–день.
    """

    ordered = df.sort_values(["user_id", "created_at"]).copy()
    ordered["day"] = ordered["created_at"].dt.date
    ordered["diff"] = ordered.groupby(["user_id", "day"])["created_at"].diff()

    active_diff = ordered["diff"].where(ordered["diff"] <= ONE_HOUR, pd.Timedelta(0))
    daily_time = active_diff.groupby([ordered["user_id"], ordered["day"]]).sum()
    daily_hours = daily_time.dt.total_seconds() / 3600

    return round(float(daily_hours.mean()), 2) if not daily_hours.empty else 0.0


def average_tasks_per_session(df: pd.DataFrame) -> float:
    """Среднее количество уникальных задач за активный сеанс.

    Новый сеанс начинается, если разница между соседними действиями пользователя
    больше одного часа. Внутри сеанса задача считается один раз по problem_id.
    """

    ordered = df.sort_values(["user_id", "created_at"]).copy()
    ordered["diff"] = ordered.groupby("user_id")["created_at"].diff()
    ordered["new_session"] = ordered["diff"].isna() | (ordered["diff"] > ONE_HOUR)
    ordered["session_id"] = ordered.groupby("user_id")["new_session"].cumsum()

    tasks_per_session = ordered.groupby(["user_id", "session_id"])["problem_id"].nunique()
    return round(float(tasks_per_session.mean()), 2) if not tasks_per_session.empty else 0.0


def peak_activity_hour(df: pd.DataFrame) -> int | None:
    """Возвращает час с максимальным числом уникальных активных пользователей."""

    if df.empty:
        return None

    hourly_users = df.assign(hour=df["created_at"].dt.hour).groupby("hour")["user_id"].nunique()
    return int(hourly_users.idxmax())


def calculate_metrics(df: pd.DataFrame) -> dict[str, float | int | None]:
    """Рассчитывает все показатели и возвращает их в одном словаре."""

    return {
        "average_solution_seconds": average_solution_time(df),
        "average_daily_active_hours": average_daily_active_hours(df),
        "average_tasks_per_session": average_tasks_per_session(df),
        "peak_activity_hour": peak_activity_hour(df),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Анализ временных данных решений задач")
    parser.add_argument("file", type=Path, help="Путь к CSV-файлу")
    parser.add_argument("--sep", default=";", help="Разделитель CSV, по умолчанию ';'")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    data = load_data(args.file, sep=args.sep)
    metrics = calculate_metrics(data)

    print(f"Среднее время успешного решения: {metrics['average_solution_seconds']:.2f} секунд")
    print(f"Среднее активное время в день: {metrics['average_daily_active_hours']:.2f} часов")
    print(f"Среднее количество задач за сеанс: {metrics['average_tasks_per_session']:.2f}")
    print(f"Самый активный час: {metrics['peak_activity_hour']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
