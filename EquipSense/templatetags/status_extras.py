# EquipSense/templatetags/status_extras.py
from django import template

register = template.Library()

# Соответствие статуса к классу Bootstrap‑badge
STATUS_COLOR_MAP = {
    'P': 'bg-warning',   # Pending – жёлтый
    'A': 'bg-success',   # Accepted – зелёный
    'R': 'bg-danger',    # Rejected – красный
}

@register.filter(name='status_color')
def status_color(status_code):
    """
    Возвращает CSS‑класс Bootstrap‑badge по коду статуса.
    Если статус неизвестен – используется нейтральный класс.
    """
    return STATUS_COLOR_MAP.get(status_code, 'bg-secondary')
