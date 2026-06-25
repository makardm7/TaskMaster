# gui.py
import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QMessageBox, QHeaderView, QFrame, QSplitter, QGroupBox,
    QCheckBox, QStatusBar
)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QColor
from task_manager import TaskManager
from storage import Storage
from models import Task

class TaskDialog(QDialog):
    """Диалоговое окно для добавления/редактирования задачи."""
    
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("✏️ Редактировать задачу" if task else "➕ Новая задача")
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if task:
            self.load_task_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Название
        title_layout = QHBoxLayout()
        title_label = QLabel("Название*:")
        title_label.setMinimumWidth(100)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Введите название задачи (обязательно)")
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)
        
        # Описание
        desc_layout = QHBoxLayout()
        desc_label = QLabel("Описание:")
        desc_label.setMinimumWidth(100)
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Введите описание задачи")
        self.desc_edit.setMaximumHeight(100)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        layout.addLayout(desc_layout)
        
        # Приоритет
        priority_layout = QHBoxLayout()
        priority_label = QLabel("Приоритет:")
        priority_label.setMinimumWidth(100)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(Task.VALID_PRIORITIES)
        self.priority_combo.setCurrentText("Средний")
        priority_layout.addWidget(priority_label)
        priority_layout.addWidget(self.priority_combo)
        priority_layout.addStretch()
        layout.addLayout(priority_layout)
        
        # Дедлайн
        deadline_layout = QHBoxLayout()
        deadline_label = QLabel("Дедлайн:")
        deadline_label.setMinimumWidth(100)
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDate(QDate.currentDate().addDays(7))
        self.deadline_edit.setDisplayFormat("yyyy-MM-dd")
        self.has_deadline = QCheckBox("Установить дедлайн")
        self.has_deadline.setChecked(False)
        self.deadline_edit.setEnabled(False)
        self.has_deadline.toggled.connect(self.deadline_edit.setEnabled)
        deadline_layout.addWidget(deadline_label)
        deadline_layout.addWidget(self.has_deadline)
        deadline_layout.addWidget(self.deadline_edit)
        deadline_layout.addStretch()
        layout.addLayout(deadline_layout)
        
        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Сохранить")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def load_task_data(self):
        """Загружает данные задачи в форму."""
        self.title_edit.setText(self.task.title)
        self.desc_edit.setText(self.task.description)
        self.priority_combo.setCurrentText(self.task.priority)
        
        if self.task.deadline:
            self.has_deadline.setChecked(True)
            date = QDate.fromString(self.task.deadline, "yyyy-MM-dd")
            self.deadline_edit.setDate(date)
    
    def get_task_data(self):
        """Возвращает данные из формы."""
        title = self.title_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        priority = self.priority_combo.currentText()
        
        deadline = None
        if self.has_deadline.isChecked():
            deadline = self.deadline_edit.date().toString("yyyy-MM-dd")
        
        return title, description, priority, deadline


class MainWindow(QMainWindow):
    """Главное окно приложения с правильными сообщениями."""
    
    def __init__(self):
        super().__init__()
        self.storage = Storage()
        self.task_manager = TaskManager(self.storage)
        self.setup_ui()
        self.refresh_task_list()
        
        # Автосохранение каждые 5 минут
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(300000)
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        self.setWindowTitle("📋 TaskMaster - Менеджер задач")
        self.setMinimumSize(1000, 600)
        
        # Стили
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                gridline-color: #eee;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QStatusBar {
                background-color: #2c3e50;
                color: white;
            }
        """)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel("📋 TaskMaster")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        about_btn = QPushButton("❓ О программе")
        about_btn.clicked.connect(self.show_about)
        about_btn.setMaximumWidth(150)
        header_layout.addWidget(about_btn)
        main_layout.addLayout(header_layout)
        
        # Панель инструментов
        toolbar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск задач...")
        self.search_input.textChanged.connect(self.on_search)
        toolbar.addWidget(self.search_input)
        
        add_btn = QPushButton("➕ Добавить")
        add_btn.clicked.connect(self.add_task)
        toolbar.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Редактировать")
        edit_btn.clicked.connect(self.edit_task)
        toolbar.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self.delete_task)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        toolbar.addWidget(delete_btn)
        
        complete_btn = QPushButton("✓ Выполнена")
        complete_btn.clicked.connect(self.toggle_complete)
        complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        toolbar.addWidget(complete_btn)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.refresh_task_list)
        toolbar.addWidget(refresh_btn)
        
        main_layout.addLayout(toolbar)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #ddd;")
        main_layout.addWidget(separator)
        
        # Основной контент
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels(["ID", "Название", "Приоритет", "Дедлайн", "Статус"])
        self.task_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.task_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.task_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.task_table.setSortingEnabled(True)
        self.task_table.doubleClicked.connect(self.edit_task)
        
        left_layout.addWidget(self.task_table)
        left_panel.setLayout(left_layout)
        
        # Правая панель
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        stats_group = QGroupBox("📊 Статистика")
        stats_layout = QVBoxLayout()
        
        self.total_label = QLabel()
        self.completed_label = QLabel()
        self.pending_label = QLabel()
        self.priority_label = QLabel()
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.completed_label)
        stats_layout.addWidget(self.pending_label)
        stats_layout.addWidget(self.priority_label)
        
        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)
        
        export_btn = QPushButton("📄 Экспорт статистики")
        export_btn.clicked.connect(self.export_statistics)
        right_layout.addWidget(export_btn)
        
        right_layout.addStretch()
        right_panel.setLayout(right_layout)
        
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([700, 250])
        
        main_layout.addWidget(content_splitter)
        central_widget.setLayout(main_layout)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ Готов к работе")
    
    def refresh_task_list(self):
        """Обновляет таблицу задач."""
        tasks = self.task_manager.get_all_tasks()
        self.update_task_table(tasks)
        self.update_statistics()
    
    def update_task_table(self, tasks):
        """Заполняет таблицу задачами."""
        self.task_table.setRowCount(len(tasks))
        
        for row, task in enumerate(tasks):
            # ID
            id_item = QTableWidgetItem(str(task.id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.task_table.setItem(row, 0, id_item)
            
            # Название
            title_item = QTableWidgetItem(task.title)
            if task.is_completed:
                title_item.setForeground(QColor("#999"))
                font = title_item.font()
                font.setStrikeOut(True)
                title_item.setFont(font)
            self.task_table.setItem(row, 1, title_item)
            
            # Приоритет
            priority_item = QTableWidgetItem(task.priority)
            priority_color = QColor(task.get_color())
            priority_item.setBackground(priority_color)
            priority_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.task_table.setItem(row, 2, priority_item)
            
            # Дедлайн
            deadline = task.deadline if task.deadline else "—"
            deadline_item = QTableWidgetItem(deadline)
            deadline_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if task.deadline and not task.is_completed:
                task_date = datetime.strptime(task.deadline, "%Y-%m-%d").date()
                if task_date < datetime.now().date():
                    deadline_item.setBackground(QColor("#ffcccc"))
                    deadline_item.setToolTip("⚠️ Просрочена!")
            
            self.task_table.setItem(row, 3, deadline_item)
            
            # Статус
            status = "✓ Выполнена" if task.is_completed else "○ В процессе"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if task.is_completed:
                status_item.setBackground(QColor("#d4edda"))
            self.task_table.setItem(row, 4, status_item)
    
    def update_statistics(self):
        """Обновляет блок статистики."""
        stats = self.task_manager.get_statistics()
        
        self.total_label.setText(f"📌 Всего задач: {stats['total']}")
        self.completed_label.setText(f"✅ Выполнено: {stats['completed']}")
        self.pending_label.setText(f"⏳ Ожидают: {stats['pending']}")
        
        priority_text = (f"📊 По приоритетам:\n"
                        f"  🔴 Высокий: {stats['high_priority']}\n"
                        f"  🟡 Средний: {stats['medium_priority']}\n"
                        f"  🟢 Низкий: {stats['low_priority']}")
        self.priority_label.setText(priority_text)
        
        self.status_bar.showMessage(
            f"Всего: {stats['total']} | Выполнено: {stats['completed']} | Ожидают: {stats['pending']}"
        )
    
    def add_task(self):
        """Добавление новой задачи с правильными сообщениями."""
        dialog = TaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, description, priority, deadline = dialog.get_task_data()
            
            if not title:
                QMessageBox.warning(
                    self,
                    "⚠️ Ошибка ввода",
                    "Название задачи обязательно для заполнения!\n\n"
                    "Пожалуйста, введите название задачи."
                )
                return
            
            try:
                task = self.task_manager.add_task(title, description, priority, deadline)
                self.refresh_task_list()
                self.status_bar.showMessage(
                    f"✅ Задача '{task.title}' (ID: {task.id}) успешно создана!", 
                    5000
                )
            except ValueError as e:
                QMessageBox.warning(self, "⚠️ Ошибка данных", str(e))
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "❌ Системная ошибка",
                    f"Не удалось создать задачу!\n\nПричина: {str(e)}\n\n"
                    "Проверьте права доступа к файлу tasks.json"
                )
    
    def edit_task(self):
        """Редактирование задачи с правильными сообщениями."""
        current_row = self.task_table.currentRow()
        if current_row < 0:
            QMessageBox.information(
                self,
                "ℹ️ Выберите задачу",
                "Пожалуйста, выберите задачу для редактирования.\n"
                "Кликните на задачу в таблице."
            )
            return
        
        task_id = int(self.task_table.item(current_row, 0).text())
        task = self.task_manager._get_task_by_id(task_id)
        
        if not task:
            QMessageBox.warning(
                self,
                "⚠️ Задача не найдена",
                f"Задача с ID {task_id} не найдена.\nВозможно, она была удалена."
            )
            self.refresh_task_list()
            return
        
        dialog = TaskDialog(self, task)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, description, priority, deadline = dialog.get_task_data()
            
            if not title:
                QMessageBox.warning(self, "⚠️ Ошибка", "Название не может быть пустым!")
                return
            
            try:
                updated_task = self.task_manager.edit_task(
                    task_id, title, description, priority, deadline
                )
                self.refresh_task_list()
                
                if updated_task:
                    self.status_bar.showMessage(
                        f"✅ Задача ID:{task_id} обновлена!", 
                        5000
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "❌ Ошибка",
                    f"Не удалось обновить задачу!\n\n{str(e)}"
                )
    
    def delete_task(self):
        """Удаление задачи с подтверждением."""
        current_row = self.task_table.currentRow()
        if current_row < 0:
            QMessageBox.information(
                self,
                "ℹ️ Выберите задачу",
                "Пожалуйста, выберите задачу для удаления."
            )
            return
        
        task_id = int(self.task_table.item(current_row, 0).text())
        task = self.task_manager._get_task_by_id(task_id)
        
        if not task:
            QMessageBox.warning(self, "⚠️ Ошибка", f"Задача с ID {task_id} не найдена!")
            return
        
        reply = QMessageBox.question(
            self,
            "⚠️ Подтверждение удаления",
            f"Вы действительно хотите удалить задачу?\n\n"
            f"📌 Название: {task.title}\n"
            f"🎯 Приоритет: {task.priority}\n"
            f"📅 Статус: {'✓ Выполнена' if task.is_completed else '○ В процессе'}\n\n"
            f"Это действие нельзя отменить!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.task_manager.delete_task(task_id)
                self.refresh_task_list()
                self.status_bar.showMessage(
                    f"✅ Задача ID:{task_id} удалена!", 
                    5000
                )
            except Exception as e:
                QMessageBox.critical(self, "❌ Ошибка", f"Не удалось удалить задачу!\n\n{str(e)}")
    
    def toggle_complete(self):
        """Отметка задачи как выполненной."""
        current_row = self.task_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "ℹ️ Выберите задачу", "Выберите задачу для изменения статуса.")
            return
        
        task_id = int(self.task_table.item(current_row, 0).text())
        
        try:
            updated_task = self.task_manager.toggle_task_completion(task_id)
            self.refresh_task_list()
            
            if updated_task:
                status_text = "✓ ВЫПОЛНЕНА" if updated_task.is_completed else "○ ВОЗОБНОВЛЕНА"
                self.status_bar.showMessage(
                    f"Статус задачи ID:{task_id} изменен на: {status_text}", 
                    5000
                )
        except Exception as e:
            QMessageBox.critical(self, "❌ Ошибка", f"Не удалось изменить статус!\n\n{str(e)}")
    
    def on_search(self):
        """Поиск задач с информативным сообщением."""
        keyword = self.search_input.text().strip()
        
        if keyword:
            tasks = self.task_manager.search_tasks(keyword)
            self.update_task_table(tasks)
            
            if not tasks:
                self.status_bar.showMessage(f"🔍 По запросу '{keyword}' ничего не найдено", 5000)
            else:
                self.status_bar.showMessage(f"🔍 Найдено задач: {len(tasks)}", 5000)
        else:
            self.refresh_task_list()
    
    def autosave(self):
        """Автосохранение данных."""
        self.task_manager.storage.save_tasks(self.task_manager.tasks)
        self.status_bar.showMessage("💾 Данные сохранены автоматически", 2000)
    
    def export_statistics(self):
        """Экспорт статистики в файл."""
        import os
        stats = self.task_manager.get_statistics()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(os.path.expanduser("~"), f"taskmaster_stats_{timestamp}.txt")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("📊 Статистика TaskMaster\n")
                f.write("=" * 40 + "\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Всего задач: {stats['total']}\n")
                f.write(f"Выполнено: {stats['completed']}\n")
                f.write(f"Ожидают: {stats['pending']}\n")
                f.write(f"Высокий приоритет: {stats['high_priority']}\n")
                f.write(f"Средний приоритет: {stats['medium_priority']}\n")
                f.write(f"Низкий приоритет: {stats['low_priority']}\n")
                
                if stats['total'] > 0:
                    completion_rate = (stats['completed'] / stats['total']) * 100
                    f.write(f"\nПроцент выполнения: {completion_rate:.1f}%\n")
            
            QMessageBox.information(
                self,
                "✅ Успешно",
                f"Статистика сохранена в файл:\n{filename}"
            )
            self.status_bar.showMessage(f"📄 Статистика экспортирована", 5000)
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Ошибка экспорта",
                f"Не удалось сохранить статистику!\n\n{str(e)}"
            )
    
    def show_about(self):
        """Показывает окно 'О программе'."""
        about_text = """
        <h2>📋 TaskMaster v1.0</h2>
        <p><b>Программа для управления персональными задачами</b></p>
        <p>Разработано в МГТУ им. Н.Э. Баумана</p>
        <p>Факультет ИУ, кафедра ИУ10</p>
        <br>
        <p><b>Возможности:</b></p>
        <ul>
            <li>✅ Создание и редактирование задач</li>
            <li>🎯 Установка приоритетов и дедлайнов</li>
            <li>🔍 Поиск и фильтрация</li>
            <li>📊 Статистика выполнения</li>
            <li>💾 Автосохранение данных</li>
        </ul>
        <br>
        <p>© 2026 Бабенко М.А., Бучнев А.Б.</p>
        """
        QMessageBox.about(self, "О программе", about_text)
    
    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        self.task_manager.storage.save_tasks(self.task_manager.tasks)
        event.accept()
