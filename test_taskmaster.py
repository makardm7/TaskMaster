import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from models import Task
from storage import Storage
from task_manager import TaskManager


class TestTask:
    
    def test_create_task_success(self):
        task = Task(id=1, title="Тестовая задача", description="Описание",
                     priority="Средний", deadline="2026-12-31")
        assert task.id == 1
        assert task.title == "Тестовая задача"
        assert task.priority == "Средний"
        assert task.is_completed == False
    
    def test_create_task_empty_title(self):
        with pytest.raises(ValueError):
            Task(id=1, title="", priority="Средний")
    
    def test_create_task_invalid_priority(self):
        with pytest.raises(ValueError):
            Task(id=1, title="Задача", priority="Недопустимый")
    
    def test_create_task_invalid_date(self):
        with pytest.raises(ValueError):
            Task(id=1, title="Задача", deadline="2026-13-40")
    
    def test_mark_completed(self):
        task = Task(id=1, title="Задача")
        assert task.is_completed == False
        task.mark_completed()
        assert task.is_completed == True
        task.mark_completed()
        assert task.is_completed == False
    
    def test_to_dict(self):
        task = Task(id=1, title="Задача", description="Описание",
                     priority="Высокий", deadline="2026-06-15", is_completed=True)
        data = task.to_dict()
        assert data["id"] == 1
        assert data["title"] == "Задача"
        assert data["priority"] == "Высокий"
        assert data["deadline"] == "2026-06-15"
        assert data["is_completed"] == True
    
    def test_from_dict(self):
        data = {"id": 2, "title": "Задача 2", "description": "Описание 2",
                "priority": "Низкий", "deadline": "2026-12-31", "is_completed": False}
        task = Task.from_dict(data)
        assert task.id == 2
        assert task.title == "Задача 2"
        assert task.priority == "Низкий"
    
    def test_get_color(self):
        task_high = Task(id=1, title="Задача", priority="Высокий")
        task_medium = Task(id=2, title="Задача", priority="Средний")
        task_low = Task(id=3, title="Задача", priority="Низкий")
        assert task_high.get_color() == "#FF6B6B"
        assert task_medium.get_color() == "#FFD93D"
        assert task_low.get_color() == "#6BCB77"


class TestStorage:
    
    def test_save_and_load(self, tmp_path):
        filepath = str(tmp_path / "tasks.json")
        storage = Storage(filepath=filepath)
        
        tasks = [
            Task(id=1, title="Задача 1"),
            Task(id=2, title="Задача 2", is_completed=True),
        ]
        
        storage.save_tasks(tasks)
        assert os.path.exists(filepath)
        
        loaded = storage.load_tasks()
        assert len(loaded) == 2
        assert loaded[0].title == "Задача 1"
        assert loaded[1].is_completed == True
    
    def test_load_empty_file(self, tmp_path):
        filepath = str(tmp_path / "empty.json")
        storage = Storage(filepath=filepath)
        tasks = storage.load_tasks()
        assert tasks == []


class TestTaskManager:
    
    def test_add_task(self, tmp_path):
        filepath = str(tmp_path / "tasks.json")
        storage = Storage(filepath=filepath)
        manager = TaskManager(storage)
        
        task = manager.add_task("Новая задача", "Описание", "Высокий", "2026-12-31")
        assert task.id == 1
        assert task.title == "Новая задача"
        assert len(manager.tasks) == 1
    
    def test_add_task_empty_title(self, tmp_path):
        filepath = str(tmp_path / "tasks.json")
        storage = Storage(filepath=filepath)
        manager = TaskManager(storage)
        
        with pytest.raises(ValueError):
            manager.add_task("", "", "Средний", None)
    
    def test_delete_task(self, tmp_path):
        filepath = str(tmp_path / "tasks.json")
        storage = Storage(filepath=filepath)
        manager = TaskManager(storage)
        
        manager.add_task("Задача 1", "", "Средний", None)
        manager.add_task("Задача 2", "", "Низкий", None)
        
        assert len(manager.tasks) == 2
        result = manager.delete_task(1)
        assert result == True
        assert len(manager.tasks) == 1
    
    def test_delete_nonexistent_task(self, tmp_path):
        filepath = str(tmp_path / "tasks.json")
        storage = Storage(filepath=filepath)
        manager = TaskManager(storage)
        
        result = manager.delete_task(999)
        assert result == False
    
    def test_toggle_completion(self, tmp_path):
        filepath = str(tmp_path / "tasks.json")
        storage = Storage(filepath=filepath)
        manager = TaskManager(storage)
        
        task = manager.add_task("Задача", "", "Средний", None)
        assert task.is_completed == False
        
        manager.toggle_task_completion(1)
        assert task.is_completed == True
        
        manager.toggle_task_completion(1)
        assert task.is_completed == False
    
    def test_search_tasks(self, tmp_path):
        filepath = str(tmp_path / "tasks.json")
        storage = Storage(filepath=filepath)
        manager = TaskManager(storage)
        
        manager.add_task("Купить молоко", "Магазин", "Средний", None)
        manager.add_task("Позвонить другу", "Связь", "Низкий", None)
        manager.add_task("Сделать курсовую", "Учеба", "Высокий", None)
        
        results = manager.search_tasks("курсовую")
        assert len(results) == 1
        assert results[0].title == "Сделать курсовую"
        
        results = manager.search_tasks("нет такого слова")
        assert len(results) == 0
    
    def test_get_all_tasks_sorted(self, tmp_path):
        filepath = str(tmp_path / "tasks.json")
        storage = Storage(filepath=filepath)
        manager = TaskManager(storage)
        
        manager.add_task("Задача 1", "", "Низкий", None)
        manager.add_task("Задача 2", "", "Высокий", None)
        manager.add_task("Задача 3", "", "Средний", None)
        
        sorted_tasks = manager.get_all_tasks()
        assert sorted_tasks[0].priority == "Высокий"
        assert sorted_tasks[1].priority == "Средний"
        assert sorted_tasks[2].priority == "Низкий"
    
    def test_get_statistics(self, tmp_path):
        filepath = str(tmp_path / "tasks.json")
        storage = Storage(filepath=filepath)
        manager = TaskManager(storage)
        
        manager.add_task("Задача 1", "", "Высокий", None)
        manager.add_task("Задача 2", "", "Средний", None)
        manager.add_task("Задача 3", "", "Низкий", None)
        
        stats = manager.get_statistics()
        assert stats["total"] == 3
        assert stats["completed"] == 0
        assert stats["pending"] == 3
        assert stats["high_priority"] == 1
