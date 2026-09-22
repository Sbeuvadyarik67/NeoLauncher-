"""
NeoTracker — диалоговые окна.

Содержит:
- CategoryDialog — создание/переименование категории
- ProductDialog — создание/редактирование товара
- ConfirmDialog — универсальное подтверждение действия
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt


# ============================================================
# ДИАЛОГ КАТЕГОРИИ
# ============================================================

class CategoryDialog(QDialog):
    """Диалог для создания или переименования категории."""

    def __init__(self, parent=None, title="Новая категория", name=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(420, 180)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        label = QLabel("Название категории:")
        label.setObjectName("section")
        layout.addWidget(label)

        self.input_field = QLineEdit()
        self.input_field.setText(name)
        self.input_field.setPlaceholderText("Например: Электроника")
        self.input_field.selectAll()
        layout.addWidget(self.input_field)

        hint = QLabel("Можно изменить позже")
        hint.setObjectName("subtitle")
        layout.addWidget(hint)

        layout.addStretch()

        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        ok_btn = QPushButton("Сохранить")
        ok_btn.setObjectName("accent")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.on_save)
        buttons.addWidget(ok_btn)

        layout.addLayout(buttons)

        self.input_field.returnPressed.connect(self.on_save)
        self.input_field.setFocus()

    def on_save(self):
        text = self.input_field.text().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым")
            return
        self.accept()

    def get_name(self):
        return self.input_field.text().strip()


# ============================================================
# УНИВЕРСАЛЬНОЕ ПОДТВЕРЖДЕНИЕ
# ============================================================

class ConfirmDialog(QMessageBox):
    """Универсальный диалог подтверждения."""

    @staticmethod
    def ask(parent, title, text, yes_text="Да", no_text="Отмена"):
        box = QMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(QMessageBox.Question)

        yes_btn = box.addButton(yes_text, QMessageBox.YesRole)
        no_btn = box.addButton(no_text, QMessageBox.NoRole)
        box.setDefaultButton(no_btn)

        box.exec()

        return box.clickedButton() == yes_btn


# ============================================================
# ДИАЛОГ ТОВАРА
# ============================================================

class ProductDialog(QDialog):
    """Диалог создания/редактирования товара."""

    def __init__(self, parent=None, title="Новый товар", product=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(480, 560)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        # ---- Название ----
        layout.addWidget(self._label("Название:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Компьютер")
        layout.addWidget(self.name_input)

        # ---- Количество ----
        layout.addWidget(self._label("Количество (шт):"))
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("0")
        layout.addWidget(self.qty_input)

        # ---- Цена ----
        layout.addWidget(self._label("Цена (₽):"))
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        layout.addWidget(self.price_input)

        # ---- Описание ----
        layout.addWidget(self._label("Описание (необязательно):"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Характеристики, заметки, детали...")
        self.desc_input.setFixedHeight(90)
        layout.addWidget(self.desc_input)

        # ---- Нет в наличии ----
        self.no_stock_check = QCheckBox("Нет в наличии (скрыть количество)")
        layout.addWidget(self.no_stock_check)

        layout.addStretch()

        # ---- Кнопки ----
        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        ok_btn = QPushButton("Сохранить")
        ok_btn.setObjectName("accent")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.on_save)
        buttons.addWidget(ok_btn)

        layout.addLayout(buttons)

        # ---- Заполнение при редактировании ----
        if product:
            self.name_input.setText(product.get("name", ""))
            self.qty_input.setText(str(product.get("quantity", 0)))
            self.price_input.setText(str(product.get("price", 0)))
            self.desc_input.setPlainText(product.get("description", "") or "")
            self.no_stock_check.setChecked(bool(product.get("no_stock", 0)))

        self.no_stock_check.stateChanged.connect(self._on_no_stock_toggle)
        self._on_no_stock_toggle()

        self.name_input.setFocus()
        self.name_input.selectAll()

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("section")
        return lbl

    def _on_no_stock_toggle(self):
        disabled = self.no_stock_check.isChecked()
        self.qty_input.setEnabled(not disabled)
        if disabled:
            self.qty_input.setText("0")

    def on_save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название товара")
            self.name_input.setFocus()
            return

        try:
            qty = int(self.qty_input.text().strip() or "0")
            if qty < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Количество должно быть целым числом ≥ 0")
            self.qty_input.setFocus()
            return

        try:
            price = float(self.price_input.text().strip().replace(",", ".") or "0")
            if price < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Цена должна быть числом ≥ 0")
            self.price_input.setFocus()
            return

        self.accept()

    def get_data(self):
        try:
            qty = int(self.qty_input.text().strip() or "0")
        except ValueError:
            qty = 0

        try:
            price = float(self.price_input.text().strip().replace(",", ".") or "0")
        except ValueError:
            price = 0.0

        return {
            "name": self.name_input.text().strip(),
            "quantity": qty,
            "price": price,
            "description": self.desc_input.toPlainText().strip(),
            "no_stock": self.no_stock_check.isChecked(),
        }