from pathlib import Path
from tempfile import TemporaryDirectory

from autograder import check_for_malicious_code, run_checker


ROOT = Path(__file__).resolve().parent
STANDARD = ROOT / "standard_solution.py"
USER = ROOT / "user_solution.py"
TESTS = ROOT / "tests.json"


def main() -> None:
    with TemporaryDirectory() as temporary_directory:
        output = Path(temporary_directory) / "output.txt"
        assert run_checker(STANDARD, USER, TESTS, output) is True
        assert output.read_text(encoding="utf-8").splitlines() == [
            "Тест пройден",
            "Тест пройден",
            "Тест пройден",
        ]

    with TemporaryDirectory() as temporary_directory:
        wrong_user = Path(temporary_directory) / "wrong_user.py"
        wrong_user.write_text("def solve(value, multiplier=2):\n    return value + multiplier\n", encoding="utf-8")
        output = Path(temporary_directory) / "output.txt"
        assert run_checker(STANDARD, wrong_user, TESTS, output) is False
        assert "Тест не пройден" in output.read_text(encoding="utf-8")

    with TemporaryDirectory() as temporary_directory:
        malicious = Path(temporary_directory) / "malicious.py"
        malicious.write_text("def solve(value):\n    return eval(value)\n", encoding="utf-8")
        output = Path(temporary_directory) / "output.txt"
        assert check_for_malicious_code(malicious.read_text(encoding="utf-8"), output) is False
        assert "Код содержит вызов eval()" in output.read_text(encoding="utf-8")

    with TemporaryDirectory() as temporary_directory:
        syntax_error = Path(temporary_directory) / "syntax_error.py"
        syntax_error.write_text("def solve(value)\n    return value\n", encoding="utf-8")
        output = Path(temporary_directory) / "output.txt"
        assert check_for_malicious_code(syntax_error.read_text(encoding="utf-8"), output) is False
        assert "Код содержит синтаксическую ошибку" in output.read_text(encoding="utf-8")

    print("Все проверки автогрейдера пройдены успешно.")


if __name__ == "__main__":
    main()
