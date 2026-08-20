from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_sessions(file_path: str | Path) -> pd.DataFrame:
    """Загружает CSV и преобразует JSON-описание сессии в структурированные столбцы."""

    raw = pd.read_csv(file_path)
    required = {"user_id", "session"}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"Отсутствуют столбцы: {sorted(missing)}")

    records: list[dict[str, Any]] = []
    for row in raw.itertuples(index=False):
        session_start, duration_seconds, pages = json.loads(row.session)
        records.append(
            {
                "user_id": row.user_id,
                "session_start": pd.to_datetime(session_start),
                "duration_seconds": float(duration_seconds),
                "pages": pages,
            }
        )

    return pd.DataFrame(records)


def get_time_to_conversion(sessions: pd.DataFrame) -> float:
    """Среднее число секунд от начала сессии до conversion.

    Сессии без целевого действия не участвуют в среднем.
    """

    conversion_times = []
    for row in sessions.itertuples(index=False):
        for page_name, page_time in row.pages:
            if page_name == "conversion":
                conversion_times.append(
                    (pd.to_datetime(page_time) - row.session_start).total_seconds()
                )
                break

    if not conversion_times:
        return 0.0
    return round(float(pd.Series(conversion_times).mean()), 2)


def get_session_duration(sessions: pd.DataFrame) -> float:
    """Средняя продолжительность сессии в секундах."""

    if sessions.empty:
        return 0.0
    return round(float(sessions["duration_seconds"].mean()), 2)


def get_daily_session_count(sessions: pd.DataFrame) -> float:
    """Среднее количество сессий на активный пользовательский день."""

    if sessions.empty:
        return 0.0

    sessions = sessions.copy()
    sessions["day"] = sessions["session_start"].dt.date
    sessions_per_day = sessions.groupby(["user_id", "day"]).size()
    return round(float(sessions_per_day.mean()), 2)


def get_average_session_count(sessions: pd.DataFrame) -> float:
    """Среднее общее количество сессий на пользователя."""

    if sessions.empty:
        return 0.0

    sessions_per_user = sessions.groupby("user_id").size()
    return round(float(sessions_per_user.mean()), 2)


def calculate_all(sessions: pd.DataFrame) -> dict[str, float]:
    return {
        "res": get_time_to_conversion(sessions),
        "res2": get_session_duration(sessions),
        "res3": get_daily_session_count(sessions),
        "res4": get_average_session_count(sessions),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Анализ пользовательских сессий")
    parser.add_argument("file", type=Path, help="Путь к sessions.csv")
    args = parser.parse_args()

    sessions = load_sessions(args.file)
    results = calculate_all(sessions)
    print(f"res = {results['res']:.2f}")
    print(f"res2 = {results['res2']:.2f}")
    print(f"res3 = {results['res3']:.2f}")
    print(f"res4 = {results['res4']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
