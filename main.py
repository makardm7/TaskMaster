import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from gui import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TaskMaster")
    app.setOrganizationName("BMSTU-IU10")
    
    # Пробуем загрузить иконку
    icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
