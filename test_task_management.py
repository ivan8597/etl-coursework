from datetime import timedelta

from task_management import Analysis, EnhancedAnalysis, Project, Task

project = Project()
task1 = Task(1, "Разработка API", "Создать API для каталога", "выполняется", timedelta(hours=8))
task2 = Task(2, "Тестирование", "Проверить интеграцию API", "ожидание", timedelta(hours=4))
task3 = Task(3, "Документация", "Описать руководство", "завершена", timedelta(hours=12))

project.add_task(task1)
project.add_task(task2)
project.add_task(task3)
assert Analysis.count_tasks(project) == 3
assert Analysis.count_tasks_by_status(project, "ожидание") == 1
assert Analysis.find_longest_task(project) is task3
assert {task.task_id for task in EnhancedAnalysis.find_tasks_with_keywords(project, ["api"])} == {1, 2}
assert project.remove_task(2) is True
assert project.remove_task(999) is False
assert len(project.get_all_tasks()) == 2

try:
    project.add_task(Task(1, "Дубликат", "", "новая", timedelta(hours=1)))
except ValueError:
    pass
else:
    raise AssertionError("Дубликат task_id должен вызывать ValueError")

assert Analysis.find_longest_task(Project()) is None
print("Все проверки пройдены успешно.")
