from __future__ import annotations

import re
from datetime import timedelta
from typing import Iterable, Iterator


class Task:
    """Задача проекта."""

    def __init__(
        self,
        task_id: int,
        name: str,
        description: str,
        status: str,
        duration: timedelta,
    ) -> None:
        self.set_task_id(task_id)
        self.set_name(name)
        self.set_description(description)
        self.set_status(status)
        self.set_duration(duration)

    def get_task_id(self) -> int:
        return self.__task_id

    def set_task_id(self, task_id: int) -> None:
        if not isinstance(task_id, int) or isinstance(task_id, bool):
            raise TypeError("task_id должен быть целым числом")
        self.__task_id = task_id

    def get_name(self) -> str:
        return self.__name

    def set_name(self, name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Название задачи не должно быть пустым")
        self.__name = name.strip()

    def get_description(self) -> str:
        return self.__description

    def set_description(self, description: str) -> None:
        if not isinstance(description, str):
            raise TypeError("Описание задачи должно быть строкой")
        self.__description = description.strip()

    def get_status(self) -> str:
        return self.__status

    def set_status(self, status: str) -> None:
        if not isinstance(status, str) or not status.strip():
            raise ValueError("Статус задачи не должен быть пустым")
        self.__status = status.strip()

    def get_duration(self) -> timedelta:
        return self.__duration

    def set_duration(self, duration: timedelta) -> None:
        if not isinstance(duration, timedelta):
            raise TypeError("duration должен быть объектом timedelta")
        if duration < timedelta(0):
            raise ValueError("Продолжительность не может быть отрицательной")
        self.__duration = duration

    task_id = property(get_task_id, set_task_id)
    name = property(get_name, set_name)
    description = property(get_description, set_description)
    status = property(get_status, set_status)
    duration = property(get_duration, set_duration)

    def __repr__(self) -> str:
        return (
            f"Task(task_id={self.task_id!r}, name={self.name!r}, "
            f"status={self.status!r}, duration={self.duration!r})"
        )


class Project:
    """Проект, содержащий набор задач с уникальными идентификаторами."""

    def __init__(self) -> None:
        self.__tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        if not isinstance(task, Task):
            raise TypeError("В проект можно добавлять только объекты Task")
        if any(existing.task_id == task.task_id for existing in self.__tasks):
            raise ValueError(f"Задача с task_id={task.task_id} уже существует")
        self.__tasks.append(task)

    def remove_task(self, task_id: int) -> bool:
        for index, task in enumerate(self.__tasks):
            if task.task_id == task_id:
                del self.__tasks[index]
                return True
        return False

    def get_all_tasks(self) -> list[Task]:
        return self.__tasks.copy()

    def __iter__(self) -> Iterator[Task]:
        return iter(self.__tasks)


class Analysis:
    """Статистический анализ задач проекта."""

    @staticmethod
    def count_tasks(project: Project) -> int:
        return sum(1 for _ in project)

    @staticmethod
    def count_tasks_by_status(project: Project, status: str) -> int:
        return sum(1 for task in project if task.status == status)

    @staticmethod
    def find_longest_task(project: Project) -> Task | None:
        return max(project, key=lambda task: task.duration, default=None)


class EnhancedAnalysis(Analysis):
    """Расширенный анализ задач по отдельным ключевым словам."""

    @staticmethod
    def find_tasks_with_keywords(
        project: Project,
        keywords: Iterable[str],
    ) -> list[Task]:
        normalized_keywords = [keyword.strip().casefold() for keyword in keywords if keyword.strip()]
        if not normalized_keywords:
            return []

        result: list[Task] = []
        for task in project:
            searchable_text = f"{task.name} {task.description}".casefold()
            words = set(re.findall(r"[\w-]+", searchable_text, flags=re.UNICODE))
            if any(keyword in words for keyword in normalized_keywords):
                result.append(task)
        return result


if __name__ == "__main__":
    project = Project()
    project.add_task(Task(1, "Разработка API", "Создать API для каталога товаров", "выполняется", timedelta(hours=8)))
    project.add_task(Task(2, "Тестирование API", "Проверить интеграцию и обработку ошибок", "ожидание", timedelta(hours=4)))
    project.add_task(Task(3, "Документация", "Описать методы API и примеры запросов", "завершена", timedelta(hours=12)))

    print(f"Всего задач: {Analysis.count_tasks(project)}")
    print(f"Выполняется: {Analysis.count_tasks_by_status(project, 'выполняется')}")
    print(f"Самая длительная задача: {Analysis.find_longest_task(project)}")
    print("Задачи по слову 'API':", EnhancedAnalysis.find_tasks_with_keywords(project, ["api"]))
