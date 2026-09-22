"""
NeoTracker — главное окно приложения.
"""

import os
import json

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget,
    QStatusBar, QLabel, QVBoxLayout
)

import database as db
from ui.styles import build_qss
from ui.category_screen import CategoryScreen
from ui.product_screen import ProductScreen


# ============================================================
# ПУТИ И НАСТРОЙКИ
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "settings.json")

DEFAULT_SETTINGS = {
    "theme": "dark",
    "window_width": 1000,
    "window_height": 700,
}


def load_settings():
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in DEFAULT_SETTINGS.items():
                    if k not in data:
                        data[k] = v
                return data
    except Exception:
        pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    try:
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Не удалось сохранить настройки: {e}")


# ============================================================
# ГЛАВНОЕ ОКНО
# ============================================================

class MainWindow(QMainWindow):
    """Главное окно NeoTracker."""

    def __init__(self):
        super().__init__()

        self.settings = load_settings()
        self.current_theme = self.settings.get("theme", "dark")

        self.setWindowTitle("NeoTracker v0.1")
        self.resize(
            self.settings.get("window_width", 1000),
            self.settings.get("window_height", 700)
        )
        self.setMinimumSize(800, 550)

        # ---- Центральный виджет ----
        central = QWidget()
        self.setCentralWidget(central)

        # ---- StackedWidget ----
        self.stack = QStackedWidget()

        # Экран 1 — категории
        self.category_screen = CategoryScreen()
        self.category_screen.category_selected.connect(self.on_category_selected)
        self.category_screen.theme_toggle_requested.connect(self.toggle_theme)
        self.stack.addWidget(self.category_screen)

        # Экран 2 — товары
        self.product_screen = ProductScreen()
        self.product_screen.back_requested.connect(self.on_back_to_categories)
        self.stack.addWidget(self.product_screen)

        # ---- Размещение ----
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

        # ---- Статусная строка ----
        status = QStatusBar()
        self.setStatusBar(status)

        self.status_label = QLabel("Готово")
        status.addWidget(self.status_label)

        status.addPermanentWidget(QLabel("NeoTracker v0.1"))

        # ---- Применяем тему ----
        self.apply_theme()

    # ============================================================
    # ТЕМА
    # ============================================================

    def apply_theme(self):
        qss = build_qss(self.current_theme)
        self.setStyleSheet(qss)
        self.category_screen.set_theme_icon(self.current_theme)

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.settings["theme"] = self.current_theme
        save_settings(self.settings)
        self.apply_theme()

        theme_name = "тёмная" if self.current_theme == "dark" else "светлая"
        self.status_label.setText(f"Тема: {theme_name}")

    # ============================================================
    # ПЕРЕХОДЫ МЕЖДУ ЭКРАНАМИ
    # ============================================================

    def on_category_selected(self, category_id):
        """Двойной клик по категории → переход к экрану товаров."""
        category = db.get_category(category_id)
        if not category:
            return

        self.product_screen.load_category(category_id)
        self.stack.setCurrentWidget(self.product_screen)
        self.status_label.setText(f"Категория: {category['name']}")

    def on_back_to_categories(self):
        """Возврат к экрану категорий."""
        self.category_screen.refresh()
        self.stack.setCurrentWidget(self.category_screen)
        self.status_label.setText("Готово")

    # ============================================================
    # СОХРАНЕНИЕ РАЗМЕРА ОКНА
    # ============================================================

    def closeEvent(self, event):
        self.settings["window_width"] = self.width()
        self.settings["window_height"] = self.height()
        save_settings(self.settings)
        super().closeEvent(event)