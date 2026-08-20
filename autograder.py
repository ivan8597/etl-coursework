from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import multiprocessing as mp
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FORBIDDEN_NAMES = {"exec"}
DEFAULT_TIMEOUT = 5.0


class CodeCheckError(ValueError):
    """Ошибка предварительной проверки пользовательского кода."""


def _write_text(output_file: str | Path, text: str) -> None:
    Path(output_file).write_text(text.rstrip() + "\n", encoding="utf-8")


def check_for_malicious_code(code: str, output_file: str | Path) -> bool:
    """Проверяет исходный код AST и записывает результат в output_file.

    AST-проверка является учебным фильтром, а не полноценной изоляцией.
    Непроверенный пользовательский код всё равно запускается только в отдельном
    процессе с ограничением времени.
    """

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_NAMES:
                raise CodeCheckError(f"Код содержит запрещенный атрибут: {node.attr}")

            if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
                raise CodeCheckError(f"Код содержит запрещенное имя: {node.id}")

            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "eval":
                raise CodeCheckError("Код содержит вызов eval()")

    except SyntaxError as error:
        message = f"Код содержит синтаксическую ошибку: {error.msg}"
        _write_text(output_file, f"Ошибка при проверке модуля user_malicious:\n{message}")
        return False
    except CodeCheckError as error:
        _write_text(output_file, f"Ошибка при проверке модуля user_malicious:\n{error}")
        return False
    except Exception as error:
        message = f"Код содержит вредоносные элементы: {error}"
        _write_text(output_file, f"Ошибка при проверке модуля user_malicious:\n{message}")
        return False

    return True


def load_module_from_path(file_path: str | Path, module_name: str):
    """Динамически загружает Python-модуль по пути к файлу."""

    path = Path(file_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Файл модуля не найден: {path}")

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Не удалось создать спецификацию модуля: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass
class ExecutionResult:
    ok: bool
    value: Any = None
    error: str | None = None
    timed_out: bool = False


def _execute_function_worker(
    file_path: str,
    module_name: str,
    function_name: str,
    args: list[Any],
    kwargs: dict[str, Any],
    result_queue,
) -> None:
    """Worker для запуска функции в отдельном процессе."""

    try:
        module = load_module_from_path(file_path, module_name)
        function = getattr(module, function_name)
        result = function(*args, **kwargs)
        result_queue.put({"ok": True, "value": result})
    except Exception as error:
        result_queue.put({"ok": False, "error": f"{type(error).__name__}: {error}"})


def execute_function(
    file_path: str | Path,
    module_name: str,
    function_name: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> ExecutionResult:
    """Запускает функцию в отдельном процессе и ограничивает время выполнения."""

    context = mp.get_context("spawn")
    result_queue = context.Queue()
    process = context.Process(
        target=_execute_function_worker,
        args=(str(Path(file_path).resolve()), module_name, function_name, args or [], kwargs or {}, result_queue),
    )
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        return ExecutionResult(ok=False, error=f"Превышено ограничение времени: {timeout} секунд", timed_out=True)

    if result_queue.empty():
        return ExecutionResult(ok=False, error=f"Процесс завершился с кодом {process.exitcode}")

    payload = result_queue.get()
    if payload["ok"]:
        return ExecutionResult(ok=True, value=payload["value"])
    return ExecutionResult(ok=False, error=payload["error"])


def _format_value(value: Any) -> str:
    return repr(value)


def load_test_cases(test_file: str | Path) -> list[dict[str, Any]]:
    """Загружает тесты из JSON-файла.

    Формат каждого теста:
    {"args": [1, 2], "kwargs": {}}
    """

    data = json.loads(Path(test_file).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Файл тестов должен содержать JSON-массив")

    cases: list[dict[str, Any]] = []
    for index, case in enumerate(data, start=1):
        if not isinstance(case, dict):
            raise ValueError(f"Тест №{index} должен быть JSON-объектом")
        cases.append({"args": case.get("args", []), "kwargs": case.get("kwargs", {})})
    return cases


def run_checker(
    standard_file: str | Path,
    user_file: str | Path,
    tests_file: str | Path,
    output_file: str | Path = "output.txt",
    function_name: str = "solve",
    timeout: float = DEFAULT_TIMEOUT,
) -> bool:
    """Сравнивает пользовательскую функцию с эталонной на всех тестах."""

    output_path = Path(output_file)
    user_code = Path(user_file).read_text(encoding="utf-8")
    if not check_for_malicious_code(user_code, output_path):
        return False

    try:
        standard_module = load_module_from_path(standard_file, "standard_solution")
        getattr(standard_module, function_name)
    except Exception as error:
        _write_text(output_path, f"Ошибка при загрузке эталонного кода: {type(error).__name__}: {error}")
        return False

    try:
        tests = load_test_cases(tests_file)
    except Exception as error:
        _write_text(output_path, f"Ошибка при загрузке тестов: {type(error).__name__}: {error}")
        return False

    messages: list[str] = []
    for case in tests:
        expected = execute_function(standard_file, "standard_solution", function_name, case["args"], case["kwargs"], timeout)
        if not expected.ok:
            _write_text(output_path, f"Ошибка при выполнении эталонного кода: {expected.error}")
            return False

        actual = execute_function(user_file, "user_solution", function_name, case["args"], case["kwargs"], timeout)
        if not actual.ok:
            _write_text(output_path, f"Ошибка при выполнении кода пользователя: {actual.error}")
            return False

        if actual.value == expected.value:
            messages.append("Тест пройден")
        else:
            messages.extend(
                [
                    "Тест не пройден",
                    f"Ожидаемый результат: {_format_value(expected.value)}",
                    f"Результат пользователя: {_format_value(actual.value)}",
                ]
            )

    _write_text(output_path, "\n".join(messages))
    return all(message == "Тест пройден" for message in messages)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Учебная система автопроверки Python-кода")
    parser.add_argument("standard_file", help="Путь к эталонному .py-файлу")
    parser.add_argument("user_file", help="Путь к пользовательскому .py-файлу")
    parser.add_argument("tests_file", help="Путь к JSON-файлу с тестовыми случаями")
    parser.add_argument("--function", default="solve", help="Имя проверяемой функции")
    parser.add_argument("--output", default="output.txt", help="Файл с результатами проверки")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Лимит секунд на один тест")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    passed = run_checker(
        args.standard_file,
        args.user_file,
        args.tests_file,
        args.output,
        args.function,
        args.timeout,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
