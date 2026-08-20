from unittest.mock import Mock, patch

from lead_funnel import Lead, SalesFunnel, Simulator

lead = Lead(1, "2026-08-20T12:00:00", "/calculator", "Расчёт", "user@example.com", "Иван")
assert lead.to_dict()["lead_id"] == 1
assert lead.current_stage is None
assert Simulator("ипотечный", "2.1").to_dict() == {"simulator_type": "ипотечный", "version": "2.1"}

funnel = SalesFunnel(["Новая заявка", "Квалификация", "Продажа"], crm_url="https://example.test/crm")

success = Mock(status_code=200)
with patch("lead_funnel.requests.post", return_value=success) as post:
    messages = funnel.process_lead(lead)
    post.assert_called_once_with("https://example.test/crm", json=lead.to_dict(), timeout=10)
assert "Данные лида успешно отправлены в CRM" in messages
assert lead.current_stage == "Квалификация"

failure = Mock(status_code=500)
with patch("lead_funnel.requests.post", return_value=failure):
    messages = funnel.process_lead(lead)
assert "Не удалось отправить данные лида в CRM" in messages
assert lead.current_stage == "Продажа"

with patch("lead_funnel.requests.post", side_effect=__import__("requests").RequestException):
    messages = funnel.process_lead(lead)
assert messages == ["Лид 1 достиг конца воронки"]
assert lead.current_stage == "Продажа"

try:
    SalesFunnel(["Этап", "Этап"])
except ValueError:
    pass
else:
    raise AssertionError("Повторяющийся этап должен вызывать ValueError")

try:
    SalesFunnel().process_lead(Lead(2, "2026-08-20", "/", "Форма", "x", "Анна"))
except ValueError:
    pass
else:
    raise AssertionError("Пустая воронка должна вызывать ValueError")

print("Все проверки пройдены успешно.")
