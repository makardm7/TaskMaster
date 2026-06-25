# task_manager.py
from typing import List, Optional
from datetime import datetime
from models import Task
from storage import Storage

class TaskManager:
    """Главный класс для управления задачами с информативными сообщениями."""
    def __init__(self, storage: Storage):
        self.storage = storage
        self.tasks: List[Task] = self.storage.load_tasks()
        self.next_id = max([task.id for task in self.tasks], default=0) + 1

    def _get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Поиск задачи по ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def add_task(self, title: str, description: str, priority: str, deadline: Optional[str]) -> Task:
        """Добавляет новую задачу с уведомлением."""
        title = title.strip()
        if not title:
            raise ValueError("❌ Название задачи не может быть пустым!")

        if deadline and deadline.strip():
            deadline = deadline.strip()
        else:
            deadline = None
            
        new_task = Task(
            id=self.next_id,
            title=title,
            description=description.strip(),
            priority=priority,
            deadline=deadline
        )
        self.next_id += 1
        self.tasks.append(new_task)
        self.storage.save_tasks(self.tasks)
        print(f"✅ Задача '{title}' успешно создана! (ID: {new_task.id})")
        return new_task

    def edit_task(self, task_id: int, new_title: Optional[str] = None,
                  new_description: Optional[str] = None,
                  new_priority: Optional[str] = None,
                  new_deadline: Optional[str] = None) -> Optional[Task]:
        """Редактирует существующую задачу с уведомлением."""
        task = self._get_task_by_id(task_id)
        if not task:
            print(f"❌ Ошибка: Задача с ID {task_id} не найдена!")
            return None

        changes_made = False
        
        if new_title is not None and new_title.strip():
            if task.title != new_title.strip():
                task.title = new_title.strip()
                changes_made = True
                
        if new_description is not None:
            if task.description != new_description.strip():
                task.description = new_description.strip()
                changes_made = True
                
        if new_priority is not None:
            if new_priority in Task.VALID_PRIORITIES:
                if task.priority != new_priority:
                    task.priority = new_priority
                    changes_made = True
            else:
                print(f"❌ Ошибка: Приоритет '{new_priority}' не изменен. Используйте: {', '.join(Task.VALID_PRIORITIES)}")
                
        if new_deadline is not None:
            if new_deadline.strip() == "":
                if task.deadline is not None:
                    task.deadline = None
                    changes_made = True
            else:
                try:
                    datetime.strptime(new_deadline.strip(), "%Y-%m-%d")
                    if task.deadline != new_deadline.strip():
                        task.deadline = new_deadline.strip()
                        changes_made = True
                except ValueError:
                    print("❌ Ошибка: Неверный формат даты. Используйте ГГГГ-ММ-ДД.")

        if changes_made:
            self.storage.save_tasks(self.tasks)
            print(f"✅ Задача с ID {task_id} успешно обновлена!")
        else:
            print(f"ℹ️ Изменения не внесены (данные не изменились).")
            
        return task

    def delete_task(self, task_id: int) -> bool:
        """Удаляет задачу по ID с подтверждением."""
        task = self._get_task_by_id(task_id)
        if not task:
            print(f"❌ Ошибка: Задача с ID {task_id} не найдена!")
            return False
        
        task_title = task.title
        self.tasks.remove(task)
        self.storage.save_tasks(self.tasks)
        print(f"✅ Задача '{task_title}' (ID: {task_id}) успешно удалена!")
        return True

    def toggle_task_completion(self, task_id: int) -> Optional[Task]:
        """Переключает статус выполнения задачи с уведомлением."""
        task = self._get_task_by_id(task_id)
        if not task:
            print(f"❌ Ошибка: Задача с ID {task_id} не найдена!")
            return None
        
        task.mark_completed()
        self.storage.save_tasks(self.tasks)
        status = "ВЫПОЛНЕНА ✓" if task.is_completed else "ВОЗОБНОВЛЕНА ○"
        print(f"✅ Статус задачи '{task.title}' (ID: {task_id}) изменен на: {status}")
        return task

    def get_all_tasks(self) -> List[Task]:
        """Возвращает все задачи, отсортированные по приоритету."""
        priority_order = {"Высокий": 3, "Средний": 2, "Низкий": 1}
        return sorted(self.tasks, key=lambda t: priority_order.get(t.priority, 0), reverse=True)

    def search_tasks(self, keyword: str) -> List[Task]:
        """Ищет задачи по ключевому слову."""
        keyword_lower = keyword.lower()
        results = [
            task for task in self.tasks
            if keyword_lower in task.title.lower() or keyword_lower in task.description.lower()
        ]
        priority_order = {"Высокий": 3, "Средний": 2, "Низкий": 1}
        return sorted(results, key=lambda t: priority_order.get(t.priority, 0), reverse=True)

    def get_statistics(self) -> dict:
        """Возвращает статистику по задачам."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.is_completed)
        high = sum(1 for t in self.tasks if t.priority == "Высокий")
        medium = sum(1 for t in self.tasks if t.priority == "Средний")
        low = sum(1 for t in self.tasks if t.priority == "Низкий")
        
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "high_priority": high,
            "medium_priority": medium,
            "low_priority": low
        }
