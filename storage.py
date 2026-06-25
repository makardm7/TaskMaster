# storage.py
import json
import os
from typing import List
from models import Task

class Storage:
    """Менеджер для сохранения и загрузки задач из JSON-файла."""
    def __init__(self, filepath: str = None):
        if filepath is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".config", "taskmaster")
            os.makedirs(config_dir, exist_ok=True)
            filepath = os.path.join(config_dir, "tasks.json")
        self.filepath = filepath

    def load_tasks(self) -> List[Task]:
        """Загружает задачи из JSON-файла с информативными сообщениями."""
        if not os.path.exists(self.filepath):
            print(f"ℹ️ Файл '{self.filepath}' не найден. Будет создан новый при сохранении.")
            return []

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    print("❌ Ошибка: Некорректный формат данных в JSON. Ожидался список задач.")
                    return []
                
                tasks = []
                for item in data:
                    try:
                        task = Task.from_dict(item)
                        tasks.append(task)
                    except Exception as e:
                        print(f"⚠️ Предупреждение: Пропущена задача {item.get('id', '?')}: {e}")
                
                print(f"✅ Успешно загружено {len(tasks)} задач из {self.filepath}")
                return tasks
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка: Файл '{self.filepath}' поврежден (некорректный JSON): {e}")
            if os.path.exists(self.filepath):
                backup_path = self.filepath + ".bak"
                os.rename(self.filepath, backup_path)
                print(f"ℹ️ Создан бэкап поврежденного файла: {backup_path}")
            return []
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {e}")
            return []

    def save_tasks(self, tasks: List[Task]):
        """Сохраняет список задач в JSON-файл с подтверждением."""
        try:
            tasks_data = [task.to_dict() for task in tasks]
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=4)
            print(f"✅ Данные сохранены в '{self.filepath}' ({len(tasks)} задач)")
        except IOError as e:
            print(f"❌ Ошибка сохранения: Нет доступа к файлу '{self.filepath}'. {e}")
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")

    def get_file_path(self) -> str:
        """Возвращает полный путь к файлу tasks.json."""
        return os.path.abspath(self.filepath)
