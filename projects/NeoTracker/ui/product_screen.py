"""
NeoTracker — экран товаров внутри категории.
"""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton,
    QMessageBox, QFrame, QLineEdit
)
from PySide6.QtCore import Qt, Signal

import database as db
from ui.dialogs import ProductDialog, ConfirmDialog
from core.export import export_category_to_excel


class ProductScreen(QWidget):
    """
    Экран товаров выбранной категории.
    Сигналы:
    - back_requested() — пользователь нажал «Назад»
    """

    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("productScreen")
        self.current_category_id = None
        self._build_ui()

    # ============================================================
    # ИНТЕРФЕЙС
    # ============================================================

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # ---- Верхняя панель ----
        top = QHBoxLayout()

        self.back_btn = QPushButton("← Назад")
        self.back_btn.setObjectName("icon")
        self.back_btn.setToolTip("Вернуться к категориям")
        self.back_btn.clicked.connect(self.back_requested.emit)
        top.addWidget(self.back_btn)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)

        self.title_label = QLabel("Товары")
        self.title_label.setObjectName("title")
        title_box.addWidget(self.title_label)

        self.subtitle_label = QLabel("")
        self.subtitle_label.setObjectName("subtitle")
        title_box.addWidget(self.subtitle_label)

        top.addLayout(title_box)
        top.addStretch()

        # Кнопка экспорта
        self.export_btn = QPushButton("📊")
        self.export_btn.setObjectName("icon")
        self.export_btn.setToolTip("Экспорт в Excel")
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

        layout.addLayout(top)

        # ---- Поле поиска ----
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setObjectName("subtitle")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию товара...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input, 1)

        self.search_clear_btn = QPushButton("✖")
        self.search_clear_btn.setObjectName("icon")
        self.search_clear_btn.setToolTip("Очистить поиск")
        self.search_clear_btn.setFixedWidth(36)
        self.search_clear_btn.setVisible(False)
        self.search_clear_btn.clicked.connect(self.on_search_clear)
        search_layout.addWidget(self.search_clear_btn)

        layout.addLayout(search_layout)

        # ---- Разделитель ----
        line = QFrame()
        line.setObjectName("hline")
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        # ---- Панель действий ----
        actions = QHBoxLayout()
        actions.setSpacing(8)

        self.add_btn = QPushButton("➕  Добавить товар")
        self.add_btn.setObjectName("accent")
        self.add_btn.clicked.connect(self.on_add)
        actions.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏  Редактировать")
        self.edit_btn.clicked.connect(self.on_edit)
        actions.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑  Удалить")
        self.delete_btn.setObjectName("danger")
        self.delete_btn.clicked.connect(self.on_delete)
        actions.addWidget(self.delete_btn)

        actions.addStretch()

        self.count_label = QLabel("0 товаров")
        self.count_label.setObjectName("subtitle")
        actions.addWidget(self.count_label)

        layout.addLayout(actions)

        # ---- Список ----
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
    # ЗАГРУЗКА ДАННЫХ
    # ============================================================

    def load_category(self, category_id):
        self.current_category_id = category_id
        self.refresh()

    def refresh(self):
        if self.current_category_id is None:
            return

        category = db.get_category(self.current_category_id)
        if not category:
            return

        self.title_label.setText(category["name"])
        self.subtitle_label.setText("Товары в этой категории")

        self.list_widget.clear()
        products = db.get_products_by_category(self.current_category_id)

        for p in products:
            item = QListWidgetItem()

            if p["no_stock"]:
                text = f"❌  {p['name']}    —    нет в наличии"
            else:
                total = p["quantity"] * p["price"]
                text = (
                    f"📦  {p['name']}    "
                    f"{p['quantity']} шт × {p['price']:,.2f} ₽    "
                    f"= {total:,.2f} ₽"
                ).replace(",", " ")

            item.setText(text)
            item.setData(Qt.UserRole, p["id"])
            item.setToolTip(p.get("description", "") or "")
            self.list_widget.addItem(item)

        count = len(products)
        self.count_label.setText(self._plural_products(count))

        qty = db.get_category_quantity(self.current_category_id)
        val = db.get_category_value(self.current_category_id)
        self.stats_label.setText(
            f"Всего в категории: {qty} шт   •   "
            f"Стоимость: {val:,.0f} ₽".replace(",", " ")
        )

        # Сбрасываем поиск при обновлении
        if self.search_input.text():
            self.search_input.clear()

        self._update_buttons_state()

    def _plural_products(self, n):
        if n % 10 == 1 and n % 100 != 11:
            return f"{n} товар"
        elif n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
            return f"{n} товара"
        else:
            return f"{n} товаров"

    def _update_buttons_state(self):
        has_selection = self.list_widget.currentItem() is not None
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    # ============================================================
    # ДЕЙСТВИЯ
    # ============================================================

    def on_add(self):
        dialog = ProductDialog(self, title="Новый товар")
        if dialog.exec() != ProductDialog.Accepted:
            return

        data = dialog.get_data()

        db.add_product(
            category_id=self.current_category_id,
            name=data["name"],
            quantity=data["quantity"],
            price=data["price"],
            description=data["description"],
            no_stock=data["no_stock"],
        )
        self.refresh()

    def on_edit(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        product_id = item.data(Qt.UserRole)
        product = db.get_product(product_id)
        if not product:
            return

        dialog = ProductDialog(self, title="Редактировать товар", product=product)
        if dialog.exec() != ProductDialog.Accepted:
            return

        data = dialog.get_data()

        db.update_product(
            product_id=product_id,
            name=data["name"],
            quantity=data["quantity"],
            price=data["price"],
            description=data["description"],
            no_stock=data["no_stock"],
        )
        self.refresh()

    def on_delete(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        product_id = item.data(Qt.UserRole)
        product = db.get_product(product_id)
        if not product:
            return

        if not ConfirmDialog.ask(
            self,
            title="Удаление товара",
            text=f"Удалить товар «{product['name']}»?",
            yes_text="Удалить",
            no_text="Отмена"
        ):
            return

        db.delete_product(product_id)
        self.refresh()

    def on_refresh(self):
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
        self.on_edit()

    # ============================================================
    # ПОИСК
    # ============================================================

    def on_search_changed(self, text):
        """Фильтрует товары по названию."""
        query = text.strip().lower()
        self.search_clear_btn.setVisible(bool(query))

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            product_id = item.data(Qt.UserRole)
            product = db.get_product(product_id)
            if not product:
                item.setHidden(True)
                continue

            name = product["name"].lower()
            if query in name:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def on_search_clear(self):
        """Очищает поле поиска."""
        self.search_input.clear()
        self.search_clear_btn.setVisible(False)

    # ============================================================
    # ЭКСПОРТ
    # ============================================================

    def on_export(self):
        """Экспорт текущей категории в Excel."""
        if self.current_category_id is None:
            return

        try:
            filepath = export_category_to_excel(self.current_category_id)
            if not filepath:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить данные категории")
                return

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