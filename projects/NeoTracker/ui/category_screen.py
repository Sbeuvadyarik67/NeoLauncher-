"""
NeoTracker — экран категорий.
"""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal

import database as db
from ui.dialogs import CategoryDialog, ConfirmDialog
from core.export import export_all_to_excel


class CategoryScreen(QWidget):
    """
    Главный экран со списком категорий.
    Сигналы:
    - category_selected(category_id) — пользователь выбрал категорию (двойной клик)
    - theme_toggle_requested() — пользователь нажал на переключатель темы
    """

    category_selected = Signal(int)
    theme_toggle_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("categoryScreen")
        self._build_ui()
        self.refresh()

    # ============================================================
    # ИНТЕРФЕЙС
    # ============================================================

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # ---- Верхняя панель ----
        top = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(0)

        title = QLabel("Категории")
        title.setObjectName("title")
        title_box.addWidget(title)

        subtitle = QLabel("Выберите категорию или создайте новую")
        subtitle.setObjectName("subtitle")
        title_box.addWidget(subtitle)

        top.addLayout(title_box)
        top.addStretch()

        # Кнопка экспорта всего склада
        self.export_btn = QPushButton("📊")
        self.export_btn.setObjectName("icon")
        self.export_btn.setToolTip("Экспорт всего склада в Excel")
        self.export_btn.setFixedWidth(44)
        self.export_btn.clicked.connect(self.on_export)
        top.addWidget(self.export_btn)

        # Кнопка обновления
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setObjectName("icon")
        self.refresh_btn.setToolTip("Обновить список")
        self.refresh_btn.setFixedWidth(44)
        self.refresh_btn.clicked.connect(self.on_refresh)
        top.addWidget(self.refresh_btn)

        # Кнопка переключения темы
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("icon")
        self.theme_btn.setToolTip("Переключить тему")
        self.theme_btn.setFixedWidth(44)
        self.theme_btn.clicked.connect(self.theme_toggle_requested.emit)
        top.addWidget(self.theme_btn)

        layout.addLayout(top)

        # ---- Разделитель ----
        line = QFrame()
        line.setObjectName("hline")
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        # ---- Панель действий ----
        actions = QHBoxLayout()
        actions.setSpacing(8)

        self.add_btn = QPushButton("➕  Новая категория")
        self.add_btn.setObjectName("accent")
        self.add_btn.clicked.connect(self.on_add)
        actions.addWidget(self.add_btn)

        self.rename_btn = QPushButton("✏  Переименовать")
        self.rename_btn.clicked.connect(self.on_rename)
        actions.addWidget(self.rename_btn)

        self.delete_btn = QPushButton("🗑  Удалить")
        self.delete_btn.setObjectName("danger")
        self.delete_btn.clicked.connect(self.on_delete)
        actions.addWidget(self.delete_btn)

        actions.addStretch()

        self.count_label = QLabel("0 категорий")
        self.count_label.setObjectName("subtitle")
        actions.addWidget(self.count_label)

        layout.addLayout(actions)

        # ---- Список категорий ----
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.list_widget.itemSelectionChanged.connect(self._update_buttons_state)
        layout.addWidget(self.list_widget, 1)

        # ---- Статистика ----
        bottom = QHBoxLayout()

        self.stats_label = QLabel("")
        self.stats_label.setObjectName("subtitle")
        bottom.addWidget(self.stats_label)

        bottom.addStretch()

        layout.addLayout(bottom)

        self._update_buttons_state()

    # ============================================================
    # ОБНОВЛЕНИЕ СПИСКА
    # ============================================================

    def refresh(self):
        """Перечитывает категории из БД и перерисовывает список."""
        self.list_widget.clear()

        categories = db.get_all_categories()

        for cat in categories:
            products = db.get_products_by_category(cat["id"])
            count = len(products)

            item = QListWidgetItem()
            item.setText(f"📁  {cat['name']}    ({count} товаров)")
            item.setData(Qt.UserRole, cat["id"])
            item.setToolTip(f"Категория: {cat['name']}")
            self.list_widget.addItem(item)

        count = len(categories)
        self.count_label.setText(self._plural_categories(count))

        total_qty = db.get_total_quantity()
        total_val = db.get_total_value()
        self.stats_label.setText(
            f"Всего товаров на складе: {total_qty} шт   •   "
            f"Общая стоимость: {total_val:,.0f} ₽".replace(",", " ")
        )

        self._update_buttons_state()

    def _plural_categories(self, n):
        if n % 10 == 1 and n % 100 != 11:
            return f"{n} категория"
        elif n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
            return f"{n} категории"
        else:
            return f"{n} категорий"

    def _update_buttons_state(self):
        has_selection = self.list_widget.currentItem() is not None
        self.rename_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    # ============================================================
    # ДЕЙСТВИЯ
    # ============================================================

    def on_add(self):
        dialog = CategoryDialog(self, title="Новая категория")
        if dialog.exec() != CategoryDialog.Accepted:
            return

        name = dialog.get_name()

        if db.category_exists(name):
            QMessageBox.warning(
                self, "Уже существует",
                f"Категория «{name}» уже есть в списке."
            )
            return

        db.add_category(name)
        self.refresh()

    def on_rename(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        category_id = item.data(Qt.UserRole)
        category = db.get_category(category_id)
        if not category:
            return

        dialog = CategoryDialog(
            self,
            title="Переименовать категорию",
            name=category["name"]
        )
        if dialog.exec() != CategoryDialog.Accepted:
            return

        new_name = dialog.get_name()

        if new_name == category["name"]:
            return

        if db.category_exists(new_name):
            QMessageBox.warning(
                self, "Уже существует",
                f"Категория «{new_name}» уже есть в списке."
            )
            return

        db.update_category(category_id, new_name)
        self.refresh()

    def on_delete(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        category_id = item.data(Qt.UserRole)
        category = db.get_category(category_id)
        if not category:
            return

        products = db.get_products_by_category(category_id)
        count = len(products)

        if count > 0:
            text = (
                f"Удалить категорию «{category['name']}»?\n\n"
                f"Вместе с ней удалятся ВСЕ товары внутри ({count} шт).\n"
                f"Это действие нельзя отменить."
            )
        else:
            text = f"Удалить категорию «{category['name']}»?"

        if not ConfirmDialog.ask(
            self,
            title="Удаление категории",
            text=text,
            yes_text="Удалить",
            no_text="Отмена"
        ):
            return

        db.delete_category(category_id)
        self.refresh()

    def on_refresh(self):
        """Ручное обновление списка из БД."""
        current_item = self.list_widget.currentItem()
        selected_id = current_item.data(Qt.UserRole) if current_item else None

        self.refresh()

        if selected_id is not None:
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if item.data(Qt.UserRole) == selected_id:
                    self.list_widget.setCurrentItem(item)
                    break

    def on_item_double_clicked(self, item):
        """Двойной клик по категории — «вход» внутрь."""
        category_id = item.data(Qt.UserRole)
        self.category_selected.emit(category_id)

    # ============================================================
    # ЭКСПОРТ
    # ============================================================

    def on_export(self):
        """Экспорт всего склада в Excel."""
        try:
            filepath = export_all_to_excel()
            QMessageBox.information(
                self,
                "Экспорт завершён",
                f"Файл сохранён:\n{filepath}"
            )
            os.startfile(os.path.dirname(filepath))
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка экспорта",
                f"Не удалось сохранить файл:\n{e}"
            )

    # ============================================================
    # ТЕМА
    # ============================================================

    def set_theme_icon(self, theme: str):
        """Меняет иконку на кнопке темы."""
        if theme == "dark":
            self.theme_btn.setText("🌙")
            self.theme_btn.setToolTip("Тёмная тема. Нажми, чтобы сделать светлую")
        else:
            self.theme_btn.setText("☀")
            self.theme_btn.setToolTip("Светлая тема. Нажми, чтобы сделать тёмную")