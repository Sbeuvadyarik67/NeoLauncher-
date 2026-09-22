"""
NeoTracker — стили и цветовые палитры.

Содержит:
- две палитры: dark и light
- функцию build_qss() — генерирует QSS-стиль для всего приложения
"""


# ============================================================
# ПАЛИТРЫ
# ============================================================

PALETTES = {
    "dark": {
        "bg":           "#0d1117",
        "bg_alt":       "#161b22",
        "bg_hover":     "#1f2630",
        "border":       "#2d3540",
        "text":         "#e6edf3",
        "text_muted":   "#8b949e",
        "accent":       "#58a6ff",
        "accent_hover": "#79b8ff",
        "danger":       "#f85149",
        "danger_hover": "#ff6b63",
        "success":      "#3fb950",
        "warning":      "#d29922",
    },
    "light": {
        "bg":           "#f6f8fa",
        "bg_alt":       "#ffffff",
        "bg_hover":     "#eaeef2",
        "border":       "#d0d7de",
        "text":         "#1f2328",
        "text_muted":   "#57606a",
        "accent":       "#0969da",
        "accent_hover": "#0a5bc4",
        "danger":       "#cf222e",
        "danger_hover": "#a40e26",
        "success":      "#1a7f37",
        "warning":      "#9a6700",
    },
}


# ============================================================
# QSS
# ============================================================

def build_qss(theme: str = "dark") -> str:
    """
    Строит QSS-стиль для приложения.
    theme: "dark" или "light"
    """
    p = PALETTES.get(theme, PALETTES["dark"])

    return f"""
/* ===== Общие ===== */
QMainWindow, QWidget {{
    background: {p['bg']};
    color: {p['text']};
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 14px;
}}

QWidget#panel {{
    background: {p['bg_alt']};
    border: 1px solid {p['border']};
    border-radius: 10px;
}}

/* ===== Заголовки ===== */
QLabel#title {{
    font-size: 22px;
    font-weight: 700;
    color: {p['text']};
    padding: 4px 0;
}}

QLabel#subtitle {{
    font-size: 13px;
    color: {p['text_muted']};
}}

QLabel#section {{
    font-size: 15px;
    font-weight: 600;
    color: {p['text']};
    padding: 4px 0;
}}

/* ===== Кнопки ===== */
QPushButton {{
    background: {p['bg_alt']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
    min-height: 20px;
}}
QPushButton:hover {{
    background: {p['bg_hover']};
    border-color: {p['accent']};
}}
QPushButton:pressed {{
    background: {p['bg']};
}}
QPushButton:disabled {{
    color: {p['text_muted']};
    border-color: {p['border']};
}}

QPushButton#accent {{
    background: {p['accent']};
    color: #ffffff;
    border: none;
    font-weight: 600;
}}
QPushButton#accent:hover {{
    background: {p['accent_hover']};
}}

QPushButton#danger {{
    background: transparent;
    color: {p['danger']};
    border: 1px solid {p['danger']};
}}
QPushButton#danger:hover {{
    background: {p['danger']};
    color: #ffffff;
}}

QPushButton#icon {{
    background: transparent;
    border: 1px solid {p['border']};
    padding: 6px 10px;
    font-size: 16px;
    min-width: 36px;
}}
QPushButton#icon:hover {{
    background: {p['bg_hover']};
}}

/* ===== Поля ввода ===== */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {p['bg']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    min-height: 22px;
    selection-background-color: {p['accent']};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {p['accent']};
}}

QLineEdit::placeholder {{
    color: {p['text_muted']};
}}

/* ===== Список ===== */
QListWidget {{
    background: {p['bg_alt']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    padding: 6px;
    outline: none;
    font-size: 14px;
}}
QListWidget::item {{
    padding: 10px 12px;
    border-radius: 6px;
    margin-bottom: 2px;
}}
QListWidget::item:hover {{
    background: {p['bg_hover']};
}}
QListWidget::item:selected {{
    background: {p['accent']};
    color: #ffffff;
}}

/* ===== Скроллбар ===== */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {p['border']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {p['text_muted']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* ===== Диалоги ===== */
QDialog {{
    background: {p['bg']};
}}
QMessageBox {{
    background: {p['bg']};
}}

/* ===== Статусная строка ===== */
QStatusBar {{
    background: {p['bg_alt']};
    color: {p['text_muted']};
    border-top: 1px solid {p['border']};
}}

/* ===== Разделители ===== */
QFrame#hline {{
    background: {p['border']};
    max-height: 1px;
    border: none;
}}

/* ===== Чекбокс ===== */
QCheckBox {{
    color: {p['text']};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {p['border']};
    background: {p['bg']};
}}
QCheckBox::indicator:checked {{
    background: {p['accent']};
    border-color: {p['accent']};
}}
"""