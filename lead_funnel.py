from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

import requests


class Lead:
    """Лид — человек, оставивший заявку на сайте."""

    def __init__(
        self,
        lead_id: int | str,
        datetime_value: datetime | str,
        page: str,
        form_title: str,
        contacts: str,
        name: str,
    ) -> None:
        self.lead_id = lead_id
        self.datetime = datetime_value
        self.page = page
        self.form_title = form_title
        self.contacts = contacts
        self.name = name
        self.current_stage: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "lead_id": self.lead_id,
            "datetime": self.datetime.isoformat() if isinstance(self.datetime, datetime) else self.datetime,
            "page": self.page,
            "form_title": self.form_title,
            "contacts": self.contacts,
            "name": self.name,
        }


class Simulator:
    """Информация о симуляторе, которым воспользовался лид."""

    def __init__(self, simulator_type: str, version: str) -> None:
        self.simulator_type = simulator_type
        self.version = version

    def to_dict(self) -> dict[str, str]:
        return {
            "simulator_type": self.simulator_type,
            "version": self.version,
        }


class SalesFunnel:
    """Воронка, обрабатывающая лидов по одному этапу за вызов."""

    def __init__(self, stages: Iterable[str] | None = None, crm_url: str = "https://itresume.com/crm/api/leads") -> None:
        self.stages: list[str] = []
        self.crm_url = crm_url
        for stage in stages or []:
            self.add_stage(stage)

    def add_stage(self, stage_name: str) -> None:
        if not isinstance(stage_name, str) or not stage_name.strip():
            raise ValueError("Название этапа не должно быть пустым")
        stage_name = stage_name.strip()
        if stage_name in self.stages:
            raise ValueError(f"Этап {stage_name!r} уже существует")
        self.stages.append(stage_name)

    def process_lead(self, lead: Lead) -> list[str]:
        if not isinstance(lead, Lead):
            raise TypeError("process_lead ожидает объект Lead")
        if not self.stages:
            raise ValueError("Нельзя обработать лида: воронка не содержит этапов")

        if lead.current_stage is None:
            stage_index = 0
        else:
            try:
                stage_index = self.stages.index(lead.current_stage)
            except ValueError as error:
                raise ValueError("Текущий этап лида отсутствует в воронке") from error

            if stage_index == len(self.stages) - 1:
                return [f"Лид {lead.lead_id} достиг конца воронки"]

        current_stage = self.stages[stage_index]
        lead.current_stage = current_stage
        messages = [f"Обработка лида {lead.lead_id} - Текущий этап: {current_stage}"]

        try:
            response = requests.post(self.crm_url, json=lead.to_dict(), timeout=10)
            if response.status_code == 200:
                messages.append("Данные лида успешно отправлены в CRM")
            else:
                messages.append("Не удалось отправить данные лида в CRM")
        except requests.RequestException:
            messages.append("Не удалось отправить данные лида в CRM")

        if stage_index + 1 < len(self.stages):
            next_stage = self.stages[stage_index + 1]
            lead.current_stage = next_stage
            messages.append(f"Перемещаем лид {lead.lead_id} на следующий этап: {next_stage}")
        else:
            messages.append(f"Лид {lead.lead_id} достиг конца воронки")

        return messages


if __name__ == "__main__":
    lead = Lead(
        lead_id=1,
        datetime_value="2026-08-20T12:00:00",
        page="/calculator",
        form_title="Заказать расчёт",
        contacts="user@example.com",
        name="Иван Иванов",
    )
    simulator = Simulator("ипотечный", "2.1")
    funnel = SalesFunnel(["Новая заявка", "Квалификация", "Продажа"])

    print(lead.to_dict())
    print(simulator.to_dict())
    print(funnel.process_lead(lead))
