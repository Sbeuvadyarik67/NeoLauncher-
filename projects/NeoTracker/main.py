"""
NeoTracker — точка входа.

Запускает приложение:
- создаёт QApplication
- инициализирует БД (создаёт таблицы, если их нет)
- создаёт и показывает главное окно
"""

import sys
from PySide6.QtWidgets import QApplication

import database as db
from ui.main_window import MainWindow


def main():
    # 1. Инициализация БД
    db.init_db()

    # 2. Создаём приложение Qt
    app = QApplication(sys.argv)
    app.setApplicationName("NeoTracker")
    app.setApplicationVersion("0.1")

    # Fusion — базовый стиль, поверх которого ляжет наш QSS
    app.setStyle("Fusion")

    # 3. Главное окно
    window = MainWindow()
    window.show()

    # 4. Запуск цикла событий
    sys.exit(app.exec())


if __name__ == "__main__":
    main()