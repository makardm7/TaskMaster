# models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    """Класс, представляющий одну задачу."""
    id: int
    title: str
    description: str = ""
    priority: str = "Средний"
    deadline: Optional[str] = None
    is_completed: bool = False

    VALID_PRIORITIES = ["Высокий", "Средний", "Низкий"]
    PRIORITY_COLORS = {
        "Высокий": "#FF6B6B",
        "Средний": "#FFD93D",
        "Низкий": "#6BCB77"
    }
    
    def __post_init__(self):
        """Валидация данных с понятными сообщениями об ошибках."""
        if not self.title or not self.title.strip():
            raise ValueError(
                "❌ Название задачи не может быть пустым!\n"
                "Пожалуйста, введите название задачи."
            )
        
        if self.priority not in self.VALID_PRIORITIES:
            raise ValueError(
                f"❌ Недопустимый приоритет: '{self.priority}'.\n"
                f"Допустимые значения: {', '.join(self.VALID_PRIORITIES)}"
            )
        
        if self.deadline is not None and self.deadline.strip() != "":
            try:
                datetime.strptime(self.deadline.strip(), "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"❌ Неверный формат даты: '{self.deadline}'.\n"
                    f"Используйте формат ГГГГ-ММ-ДД (например: 2026-12-31)"
                )

    def mark_completed(self):
        """Переключает статус выполнения задачи."""
        self.is_completed = not self.is_completed

    def to_dict(self):
        """Сериализует задачу в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "deadline": self.deadline,
            "is_completed": self.is_completed,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Десериализует задачу из словаря."""
        return cls(
            id=data.get("id"),
            title=data.get("title", "Без названия"),
            description=data.get("description", ""),
            priority=data.get("priority", "Средний"),
            deadline=data.get("deadline"),
            is_completed=data.get("is_completed", False),
        )

    def get_color(self):
        """Возвращает цвет приоритета."""
        return self.PRIORITY_COLORS.get(self.priority, "#FFFFFF")
