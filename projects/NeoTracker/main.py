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
    # 1. Автобэкап (до любых изменений в БД)
    db.daily_backup()

    # 2. Инициализация БД
    db.init_db()

    # 3. Создаём приложение Qt
    app = QApplication(sys.argv)
    app.setApplicationName("NeoTracker")
    app.setApplicationVersion("0.1")

    # Fusion — базовый стиль, поверх которого ляжет наш QSS
    app.setStyle("Fusion")

    # 4. Главное окно
    window = MainWindow()
    window.show()

    # 5. Запуск цикла событий
    sys.exit(app.exec())


if __name__ == "__main__":
    main()