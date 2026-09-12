import sys
import json
import os
import threading
import requests
import subprocess
import time
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# ======================================================
# ЯЗЫКИ
# ======================================================

LANGUAGES = {
    "ru": {
        "title": "✦ NeoBrain", "settings": "✦ Настройки", "hide": "◀ Скрыть", "show": "▶ Показать",
        "theme": "🎯 Тема", "style": "🎨 Стиль", "style_default": "По умолчанию",
        "model": "🧠 Модель", "refresh": "🔄 Обновить модели",
        "stream": "💬 Потоковый ответ", "stream_check": "Включить плавный вывод",
        "character": "👤 Персонаж", "create_character": "➕ Создать персонажа",
        "clear": "🗑 Очистить чат", "send_placeholder": "Напишите сообщение… (Enter для отправки)",
        "status_ready": "Готов", "status_checking": "⏳ Проверка Ollama...",
        "status_ollama_ok": "✅ Ollama запущен", "status_ollama_error": "⚠️ Ollama не доступен",
        "status_launch": "⏳ Запуск Ollama...", "status_ollama_fail": "⚠️ Не удалось запустить Ollama",
        "status_ollama_started": "✅ Ollama запущен", "status_typing": "💬 Печатает...",
        "status_error": "❌ Ошибка: {e}",
        "character_title": "✦ Создать персонажа", "character_name": "👤 Имя персонажа:",
        "character_gender": "⚧ Пол:", "character_male": "♂ Мужской", "character_female": "♀ Женский",
        "character_personality": "🧠 Характер (личность):",
        "character_desc": "📝 Описание (как отвечает, стиль речи, манера):",
        "character_create": "✅ Создать", "character_cancel": "Отмена",
        "character_error": "Ошибка", "character_error_name": "Введите имя персонажа!",
        "character_created": "✅ Создан персонаж: {name} ({gender})",
        "msg_count": "Сообщений: {count}", "clear_confirm": "Очистка",
        "clear_confirm_text": "Удалить всю историю чата?", "chat_cleared": "Чат очищен.",
        "model_changed": "Модель изменена на: {model}",
        "theme_changed": "Тема: {theme}", "style_changed": "Стиль: {style}",
        "welcome": "Привет! Я твой AI-помощник. Начни диалог или выбери тему.",
    },
    "en": {
        "title": "✦ NeoBrain", "settings": "✦ Settings", "hide": "◀ Hide", "show": "▶ Show",
        "theme": "🎯 Theme", "style": "🎨 Style", "style_default": "Default",
        "model": "🧠 Model", "refresh": "🔄 Refresh models",
        "stream": "💬 Stream mode", "stream_check": "Enable smooth output",
        "character": "👤 Character", "create_character": "➕ Create character",
        "clear": "🗑 Clear chat", "send_placeholder": "Type a message… (Enter to send)",
        "status_ready": "Ready", "status_checking": "⏳ Checking Ollama...",
        "status_ollama_ok": "✅ Ollama running", "status_ollama_error": "⚠️ Ollama unavailable",
        "status_launch": "⏳ Starting Ollama...", "status_ollama_fail": "⚠️ Failed to start Ollama",
        "status_ollama_started": "✅ Ollama started", "status_typing": "💬 Typing...",
        "status_error": "❌ Error: {e}",
        "character_title": "✦ Create character", "character_name": "👤 Character name:",
        "character_gender": "⚧ Gender:", "character_male": "♂ Male", "character_female": "♀ Female",
        "character_personality": "🧠 Personality:",
        "character_desc": "📝 Description (style, manner):",
        "character_create": "✅ Create", "character_cancel": "Cancel",
        "character_error": "Error", "character_error_name": "Enter character name!",
        "character_created": "✅ Character created: {name} ({gender})",
        "msg_count": "Messages: {count}", "clear_confirm": "Clear",
        "clear_confirm_text": "Delete entire chat history?", "chat_cleared": "Chat cleared.",
        "model_changed": "Model changed to: {model}",
        "theme_changed": "Theme: {theme}", "style_changed": "Style: {style}",
        "welcome": "Hi! I'm your AI assistant. Start a conversation or choose a theme.",
    }
}

# ======================================================
# ПАЛИТРЫ ТЕМ
# ======================================================

PALETTES = {
    "🌆 Неон":      {"bg": "#0a0512", "card": "rgba(20,5,30,0.95)", "border": "rgba(255,45,138,0.5)", "accent": "#ff2d8a", "accent2": "#d11a6a", "text": "#ffb0d0", "muted": "#ff6b9a", "input_bg": "rgba(10,5,20,0.95)", "input_border": "rgba(255,45,138,0.3)", "scroll_bg": "rgba(0,0,0,0.3)", "scroll_handle": "rgba(255,45,138,0.4)", "scroll_hover": "rgba(255,45,138,0.6)", "light": False},
    "🖤 Тёмная":    {"bg": "#0a0a18", "card": "rgba(15,15,35,0.95)", "border": "rgba(79,172,254,0.1)", "accent": "#4facfe", "accent2": "#3b82f6", "text": "#eeeef8", "muted": "#888", "input_bg": "rgba(8,8,20,0.95)", "input_border": "rgba(42,42,90,0.3)", "scroll_bg": "rgba(0,0,0,0.3)", "scroll_handle": "rgba(255,255,255,0.2)", "scroll_hover": "rgba(255,255,255,0.3)", "light": False},
    "🌃 Ночная":    {"bg": "#0a0a20", "card": "rgba(10,10,30,0.95)", "border": "rgba(100,100,200,0.1)", "accent": "#6c5ce7", "accent2": "#5649b5", "text": "#d0d0f0", "muted": "#888", "input_bg": "rgba(8,8,25,0.95)", "input_border": "rgba(60,60,120,0.3)", "scroll_bg": "rgba(0,0,0,0.3)", "scroll_handle": "rgba(255,255,255,0.15)", "scroll_hover": "rgba(255,255,255,0.25)", "light": False},
    "💻 Киберпанк": {"bg": "#0a0f1a", "card": "rgba(10,15,30,0.95)", "border": "rgba(0,200,255,0.3)", "accent": "#00c8ff", "accent2": "#0099cc", "text": "#88ddff", "muted": "#44aacc", "input_bg": "rgba(5,10,20,0.95)", "input_border": "rgba(0,200,255,0.25)", "scroll_bg": "rgba(0,0,0,0.3)", "scroll_handle": "rgba(0,200,255,0.3)", "scroll_hover": "rgba(0,200,255,0.5)", "light": False},
    "🔮 Фиолетовая":{"bg": "#0a0518", "card": "rgba(20,10,40,0.95)", "border": "rgba(160,120,255,0.2)", "accent": "#8b5cf6", "accent2": "#6d4bd6", "text": "#d0c0f0", "muted": "#888", "input_bg": "rgba(10,5,30,0.95)", "input_border": "rgba(160,120,255,0.2)", "scroll_bg": "rgba(0,0,0,0.3)", "scroll_handle": "rgba(160,120,255,0.25)", "scroll_hover": "rgba(160,120,255,0.4)", "light": False},
    "☀️ Светлая":   {"bg": "#f0f4f8", "card": "rgba(255,255,255,0.92)", "border": "rgba(200,210,220,0.4)", "accent": "#3498db", "accent2": "#2980b9", "text": "#2c3e50", "muted": "#888", "input_bg": "#ffffff", "input_border": "#dbe2e8", "scroll_bg": "rgba(200,200,200,0.3)", "scroll_handle": "rgba(0,0,0,0.2)", "scroll_hover": "rgba(0,0,0,0.3)", "light": True},
    "🌸 Розовая":   {"bg": "#fdf0f5", "card": "rgba(255,245,250,0.95)", "border": "rgba(255,180,200,0.4)", "accent": "#e87a9a", "accent2": "#d06a8a", "text": "#4a2a3a", "muted": "#888", "input_bg": "#ffffff", "input_border": "#f0d0dd", "scroll_bg": "rgba(200,200,200,0.3)", "scroll_handle": "rgba(0,0,0,0.15)", "scroll_hover": "rgba(0,0,0,0.25)", "light": True},
    "🌊 Морская":   {"bg": "#e8f4f8", "card": "rgba(240,250,255,0.95)", "border": "rgba(100,200,220,0.4)", "accent": "#3aa8c8", "accent2": "#2a98b8", "text": "#1a3a4a", "muted": "#888", "input_bg": "#ffffff", "input_border": "#c0e0e8", "scroll_bg": "rgba(200,200,200,0.3)", "scroll_handle": "rgba(0,0,0,0.15)", "scroll_hover": "rgba(0,0,0,0.25)", "light": True},
    "🌿 Мятная":    {"bg": "#e8f5f0", "card": "rgba(240,255,248,0.95)", "border": "rgba(100,210,180,0.4)", "accent": "#3aaa8a", "accent2": "#2a9a7a", "text": "#1a3a32", "muted": "#888", "input_bg": "#ffffff", "input_border": "#c0e8dd", "scroll_bg": "rgba(200,200,200,0.3)", "scroll_handle": "rgba(0,0,0,0.15)", "scroll_hover": "rgba(0,0,0,0.25)", "light": True},
    "☕ Кремовая":  {"bg": "#f5eee8", "card": "rgba(255,248,240,0.95)", "border": "rgba(210,190,170,0.4)", "accent": "#b89070", "accent2": "#a88060", "text": "#3a2a1a", "muted": "#888", "input_bg": "#ffffff", "input_border": "#e0d0c0", "scroll_bg": "rgba(200,200,200,0.3)", "scroll_handle": "rgba(0,0,0,0.15)", "scroll_hover": "rgba(0,0,0,0.25)", "light": True},
}

THEME_PROMPTS = {
    "🌆 Неон": "Ты полезный ассистент. Отвечай на русском языке.",
    "🖤 Тёмная": "Ты полезный ассистент. Отвечай на русском языке.",
    "🌃 Ночная": "Ты спокойный собеседник. Отвечай мягко и вдумчиво.",
    "💻 Киберпанк": "Ты хакер из 2077. Говори дерзко и стильно.",
    "🔮 Фиолетовая": "Ты мистический помощник. Говори загадочно.",
    "☀️ Светлая": "Ты дружелюбный помощник. Отвечай тепло и открыто.",
    "🌸 Розовая": "Ты нежный собеседник. Говори мягко и с заботой.",
    "🌊 Морская": "Ты спокойный и уравновешенный. Как морской бриз.",
    "🌿 Мятная": "Ты свежий и бодрый. Отвечай энергично.",
    "☕ Кремовая": "Ты уютный собеседник. Говори тепло и по-домашнему.",
}

STYLES = {
    "По умолчанию": {"radius": 18, "btn_radius": 10, "send_radius": 30,
                     "font": "'Segoe UI', sans-serif", "font_size": 15, "input_font": 15},
    "🌃 Neon":      {"radius": 18, "btn_radius": 10, "send_radius": 30,
                     "font": "'Segoe UI', sans-serif", "font_size": 15, "input_font": 15},
    "☁️ Claude":    {"radius": 16, "btn_radius": 8,  "send_radius": 26,
                     "font": "'Georgia', serif", "font_size": 15, "input_font": 15},
    "🪟 Glass":     {"radius": 18, "btn_radius": 10, "send_radius": 30,
                     "font": "'Segoe UI', sans-serif", "font_size": 15, "input_font": 15},
    "💻 Terminal":  {"radius": 4,  "btn_radius": 2,  "send_radius": 4,
                     "font": "'Consolas', 'Courier New', monospace", "font_size": 14, "input_font": 14},
}


def get_effective_palette(palette_key: str, style_key: str) -> dict:
    p = dict(PALETTES.get(palette_key, PALETTES["🌆 Неон"]))

    if style_key == "💻 Terminal":
        p.update({"bg": "#0c0c0c", "card": "rgba(20,20,20,0.95)",
                  "border": "rgba(0,255,0,0.15)", "accent": "#00ff00", "accent2": "#00cc00",
                  "text": "#00cc00", "muted": "#008800",
                  "input_bg": "rgba(0,0,0,0.8)", "input_border": "rgba(0,255,0,0.2)",
                  "scroll_handle": "rgba(0,255,0,0.2)", "scroll_hover": "rgba(0,255,0,0.4)",
                  "scroll_bg": "rgba(0,0,0,0.5)", "light": False})
    elif style_key == "🪟 Glass":
        p.update({"bg": "#1a1a2e", "card": "rgba(255,255,255,0.06)",
                  "border": "rgba(255,255,255,0.1)", "text": "#e0e0e0", "muted": "#c0c0d0",
                  "input_bg": "rgba(255,255,255,0.06)", "input_border": "rgba(255,255,255,0.1)",
                  "scroll_handle": "rgba(255,255,255,0.15)", "scroll_hover": "rgba(255,255,255,0.25)",
                  "light": False})
    elif style_key == "☁️ Claude":
        p.update({"bg": "#f9f8f6", "card": "rgba(255,255,255,0.95)",
                  "border": "rgba(200,190,180,0.3)", "accent": "#d97757", "accent2": "#c2654a",
                  "text": "#3d3d3d", "muted": "#999",
                  "input_bg": "#ffffff", "input_border": "#e5dfd8",
                  "scroll_bg": "rgba(0,0,0,0.05)",
                  "scroll_handle": "rgba(0,0,0,0.15)", "scroll_hover": "rgba(0,0,0,0.25)",
                  "light": True})

    return p


def build_qss(palette_key: str, style_key: str) -> str:
    p = get_effective_palette(palette_key, style_key)
    s = STYLES.get(style_key, STYLES["По умолчанию"])

    ff = s["font"]
    fs = s["font_size"]
    ifs = s["input_font"]
    r = s["radius"]
    br = s["btn_radius"]
    sr = s["send_radius"]

    accent_text = "white"
    if palette_key == "💻 Киберпанк" and style_key != "💻 Terminal":
        accent_text = "#0a0f1a"
    if style_key == "💻 Terminal":
        accent_text = "#0c0c0c"

    return f"""
QMainWindow {{ background: {p['bg']}; }}
QWidget {{ font-family: {ff}; }}
QWidget#card {{
    background: {p['card']};
    border: 1px solid {p['border']};
    border-radius: {r}px;
}}
QWidget#sidebar {{
    background: {p['card']};
    border-right: 1px solid {p['border']};
}}
QPushButton {{
    background: {p['accent']};
    color: {accent_text};
    border: none;
    border-radius: {br}px;
    padding: 10px;
    font-weight: 600;
    font-family: {ff};
    font-size: 13px;
}}
QPushButton:hover {{ background: {p['accent2']}; }}
QPushButton:disabled {{ background: rgba(120,120,120,0.3); color: #888; }}
QPushButton:checked {{
    background: {p['accent']};
    color: {accent_text};
    border: 2px solid {p['accent2']};
    font-weight: 700;
}}

QPushButton#send_btn {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {p['accent']}, stop:1 {p['accent2']});
    color: {accent_text};
    border: none;
    border-radius: {sr}px;
    min-width: 52px; min-height: 52px;
    font-size: 18px; font-weight: 700;
}}
QPushButton#send_btn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {p['accent2']}, stop:1 {p['accent']});
}}

QPushButton#stop_btn {{
    background: #ff4757; color: white;
    border: none; border-radius: {sr}px;
    min-width: 52px; min-height: 52px;
    font-size: 20px; font-weight: 700;
}}
QPushButton#stop_btn:hover {{ background: #ff6b7b; }}

QPushButton#clear_btn {{
    background: #ff4757; color: white;
    border: none; border-radius: {br}px;
    padding: 11px; font-weight: 600;
}}
QPushButton#clear_btn:hover {{ background: #ff6b7b; }}

QPushButton#refresh_btn {{
    background: rgba(120,120,120,0.12);
    color: {p['accent']};
    border: 1px solid {p['border']};
    border-radius: {br}px;
    padding: 7px;
    font-size: 12px; font-weight: 500;
}}
QPushButton#refresh_btn:hover {{ background: rgba(120,120,120,0.25); }}

QPushButton#sidebar_trigger {{
    background: {p['card']};
    border: 1px solid {p['border']};
    border-left: none;
    border-radius: 0 {br}px {br}px 0;
    color: {p['accent']};
    font-size: 13px; font-weight: bold;
}}

QLineEdit {{
    background: {p['input_bg']};
    border: 1px solid {p['input_border']};
    color: {p['text']};
    padding: 10px 14px;
    border-radius: {br}px;
    font-size: 14px;
    font-family: {ff};
}}
QLineEdit:focus {{ border: 2px solid {p['accent']}; }}

QLineEdit#input_field {{
    background: {p['input_bg']};
    border: 2px solid {p['input_border']};
    color: {p['text']};
    padding: 14px 20px;
    border-radius: {br}px;
    font-size: {ifs}px;
    font-family: {ff};
}}
QLineEdit#input_field:focus {{ border: 2px solid {p['accent']}; }}

QTextEdit {{
    background: {p['input_bg']};
    border: 1px solid {p['input_border']};
    color: {p['text']};
    padding: 10px 14px;
    border-radius: {br}px;
    font-size: 14px;
    font-family: {ff};
}}
QTextEdit:focus {{ border: 1px solid {p['accent']}; }}

QComboBox {{
    background: {p['input_bg']};
    border: 1px solid {p['input_border']};
    color: {p['text']};
    padding: 8px 14px;
    border-radius: {br}px;
    min-height: 38px;
    font-family: {ff};
}}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {p['input_bg']};
    color: {p['text']};
    selection-background-color: {p['accent']};
    border: 1px solid {p['border']};
}}

QLabel {{ color: {p['text']}; font-family: {ff}; }}
QLabel#muted {{ color: {p['muted']}; font-size: 12px; font-weight: 600; }}
QLabel#title {{ color: {p['accent']}; font-size: 22px; font-weight: 700; font-family: {ff}; }}
QLabel#panel_title {{ color: {p['accent']}; font-size: 19px; font-weight: 700; font-family: {ff}; }}
QLabel#separator {{ background: {p['border']}; }}

QCheckBox {{ color: {p['text']}; font-size: 13px; font-family: {ff}; }}

QScrollArea {{ border: none; background: transparent; }}

QScrollBar:vertical {{
    background: {p['scroll_bg']};
    width: 6px; border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {p['scroll_handle']};
    border-radius: 3px;
}}
QScrollBar::handle:vertical:hover {{ background: {p['scroll_hover']}; }}

QStatusBar {{ color: {p['muted']}; font-family: {ff}; }}
QStatusBar QLabel {{ color: {p['muted']}; }}

QMenu {{
    background: {p['card']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 6px;
    padding: 4px;
}}
QMenu::item {{ padding: 6px 20px; border-radius: 4px; }}
QMenu::item:selected {{ background: {p['accent']}; color: {accent_text}; }}

QMessageBox {{ background: {p['bg']}; }}
QMessageBox QLabel {{ color: {p['text']}; }}
QMessageBox QPushButton {{
    background: {p['accent']}; color: {accent_text};
    border: none; border-radius: 6px; padding: 8px 18px; min-width: 70px;
}}
"""


# ======================================================
# OVERLAY ДЛЯ ПЛАВНОЙ СМЕНЫ ТЕМЫ
# ======================================================

class FadeOverlay(QWidget):
    """Полупрозрачный overlay поверх окна для плавной смены темы."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.0)
        self.setGraphicsEffect(self._effect)
        self._color = "#000000"
        self.setStyleSheet(f"background: {self._color};")
        self.hide()

    def set_color(self, color: str):
        self._color = color
        self.setStyleSheet(f"background: {color};")

    def set_opacity(self, value: float):
        self._effect.setOpacity(max(0.0, min(1.0, value)))


# ======================================================
# ПУЗЫРЁК СООБЩЕНИЯ
# ======================================================

class MessageBubble(QWidget):
    def __init__(self, text, is_user=False, sender="", palette_key="🌆 Неон",
                 style_key="По умолчанию", show_sender=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.sender_text = sender
        self.show_sender = show_sender

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 6, 10, 6)
        main_layout.setSpacing(0)

        bubble_container = QWidget()
        bubble_container.setStyleSheet("background: transparent; border: none;")
        bubble_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        bl = QVBoxLayout(bubble_container)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(3)

        self.bubble = QWidget()
        self.bubble.setMaximumWidth(680)
        self.bubble.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        inner = QVBoxLayout(self.bubble)
        inner.setContentsMargins(18, 14, 18, 14)
        inner.setSpacing(4)

        self.name_label = QLabel(sender)
        self.name_label.setStyleSheet("font-size: 11px; font-weight: 700; background: transparent;")
        inner.addWidget(self.name_label)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-size: 15px; background: transparent;")
        inner.addWidget(self.label)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 50 if is_user else 35))
        shadow.setOffset(0, 3)
        self.bubble.setGraphicsEffect(shadow)

        bl.addWidget(self.bubble)

        if is_user:
            main_layout.addStretch()
            main_layout.addWidget(bubble_container)
        else:
            main_layout.addWidget(bubble_container)
            main_layout.addStretch()

        self.apply_palette(palette_key, style_key)

    def apply_palette(self, palette_key, style_key):
        p = get_effective_palette(palette_key, style_key)
        s = STYLES.get(style_key, STYLES["По умолчанию"])
        radius = s["radius"]
        is_light = p.get("light", False)

        if self.is_user:
            self.bubble.setStyleSheet(f"""
                QWidget {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {p['accent']}, stop:1 {p['accent2']});
                    border-radius: {radius}px;
                    border-top-right-radius: 4px;
                }}
            """)
            text_color = "white"
            name_color = "rgba(255,255,255,0.8)"
        else:
            if is_light:
                self.bubble.setStyleSheet(f"""
                    QWidget {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(230,230,240,0.9), stop:1 rgba(210,210,225,0.7));
                        border-radius: {radius}px;
                        border-top-left-radius: 4px;
                        border: 1px solid rgba(180,180,190,0.3);
                    }}
                """)
                text_color = "#1a1a1a"
                name_color = "rgba(0,0,0,0.5)"
            else:
                self.bubble.setStyleSheet(f"""
                    QWidget {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(255,255,255,0.14), stop:1 rgba(255,255,255,0.07));
                        border-radius: {radius}px;
                        border-top-left-radius: 4px;
                        border: 1px solid rgba(255,255,255,0.06);
                    }}
                """)
                text_color = "#eeeef8"
                name_color = "rgba(255,255,255,0.55)"

        self.label.setStyleSheet(f"color: {text_color}; font-size: 15px; background: transparent;")
        self.name_label.setStyleSheet(f"color: {name_color}; font-size: 11px; font-weight: 700; background: transparent;")

        if self.show_sender and self.sender_text:
            self.name_label.setText(self.sender_text)
            self.name_label.setVisible(True)
        else:
            self.name_label.setVisible(False)

    def set_text(self, text):
        self.label.setText(text)


# ======================================================
# ОСНОВНОЕ ОКНО
# ======================================================

class NeoBrainChat(QMainWindow):

    sig_update_bubble = Signal(object, str)
    sig_update_model_combo = Signal(list)
    sig_scroll = Signal()

    def __init__(self):
        super().__init__()

        self.settings_lock = threading.Lock()
        self.settings = self.load_settings()
        self.lang = self.settings.get("lang", "ru")
        self.T = LANGUAGES[self.lang]

        self.model = self.settings.get("model", "llama3.2:3b")
        self.ollama_url = self.settings.get("ollama_url", "http://localhost:11434")
        self.temperature = self.settings.get("temperature", 0.7)
        self.current_theme = self.settings.get("theme", "🌆 Неон")
        self.current_style = self.settings.get("style", "По умолчанию")
        self.message_history = self.settings.get("history", [])
        self.msg_counter = len(self.message_history)

        self.sidebar_visible = True
        self.sidebar_width = 270
        self.models = ["llama3.2:3b"]
        self.characters = self.settings.get("characters", {})
        self.current_character = self.settings.get("current_character", None)

        self.is_generating = False
        self.stop_generation = False
        self._theme_animating = False
        self._overlay = None

        self.setWindowTitle(self.T["title"])
        self.resize(1200, 800)
        self.setMinimumSize(960, 600)

        self.setup_ui()

        self._overlay = FadeOverlay(self)
        self._overlay.resize(self.size())

        self.sig_update_bubble.connect(self._do_update_bubble)
        self.sig_update_model_combo.connect(self._do_update_model_combo)
        self.sig_scroll.connect(self._do_scroll)

        self._apply_qss_now()

        self.status_text.setText(self.T["status_checking"])
        threading.Thread(target=self._check_ollama_async, daemon=True).start()

        if self.message_history:
            for msg in self.message_history:
                self.add_message(msg.get("sender", "NeoBrain"), msg.get("text", ""), restore=True)
        else:
            self.add_system_message("✦ NeoBrain", self.T["welcome"])

    # ============================================================
    # ПРИМЕНЕНИЕ QSS
    # ============================================================

    def _apply_qss_now(self):
        qss = build_qss(self.current_theme, self.current_style)
        self.setStyleSheet("")
        self.setStyleSheet(qss)
        self._refresh_bubbles_palette()
        self.theme_btn.setText(f"🎯 {self.current_theme}")
        self.style_btn.setText(f"🎨 {self.current_style}")
        self.status_label.setText(f"🎯 {self.current_theme} • 🎨 {self.current_style}")
        self.update()
        self.repaint()

    def _refresh_bubbles_palette(self):
        for i in range(self.chat_container_layout.count()):
            item = self.chat_container_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), MessageBubble):
                item.widget().apply_palette(self.current_theme, self.current_style)

    # ============================================================
    # ПЛАВНАЯ СМЕНА ТЕМЫ
    # ============================================================

    def _apply_qss_smooth(self):
        if self._theme_animating:
            return
        self._theme_animating = True

        if self._overlay is None:
            self._overlay = FadeOverlay(self)
        self._overlay.resize(self.size())

        next_palette = get_effective_palette(self.current_theme, self.current_style)
        overlay_color = "#ffffff" if next_palette.get("light", False) else "#000000"
        self._overlay.set_color(overlay_color)
        self._overlay.set_opacity(0.0)
        self._overlay.raise_()
        self._overlay.show()

        self._fade_in = QPropertyAnimation(self._overlay._effect, b"opacity")
        self._fade_in.setDuration(130)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(0.45)
        self._fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self._fade_in.finished.connect(self._smooth_middle)
        self._fade_in.start()

    def _smooth_middle(self):
        qss = build_qss(self.current_theme, self.current_style)
        self.setStyleSheet("")
        self.setStyleSheet(qss)
        self._refresh_bubbles_palette()
        self.theme_btn.setText(f"🎯 {self.current_theme}")
        self.style_btn.setText(f"🎨 {self.current_style}")
        self.status_label.setText(f"🎯 {self.current_theme} • 🎨 {self.current_style}")
        self.update()
        self.repaint()

        self._fade_out = QPropertyAnimation(self._overlay._effect, b"opacity")
        self._fade_out.setDuration(220)
        self._fade_out.setStartValue(0.45)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.InCubic)
        self._fade_out.finished.connect(self._smooth_done)
        self._fade_out.start()

    def _smooth_done(self):
        self._overlay.hide()
        self._theme_animating = False

    # ============================================================
    # НАСТРОЙКИ
    # ============================================================

    def load_settings(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neobrain_settings.json")
        default = {
            "ollama_url": "http://localhost:11434", "model": "llama3.2:3b", "temperature": 0.7,
            "theme": "🌆 Неон", "style": "По умолчанию",
            "current_character": None, "characters": {}, "history": [],
            "auto_save": True, "stream_mode": True, "max_tokens": 512, "lang": "ru"
        }
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for k, v in default.items():
                        if k not in data:
                            data[k] = v
                    return data
        except Exception:
            pass
        return default

    def save_settings(self):
        try:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neobrain_settings.json")
            with self.settings_lock:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def save_history(self):
        if self.settings.get("auto_save", True):
            self.settings["history"] = self.message_history[-100:]
            self.save_settings()

    # ============================================================
    # OLLAMA
    # ============================================================

    def _check_ollama_async(self):
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if resp.status_code == 200:
                QMetaObject.invokeMethod(self, "_set_status_ok", Qt.QueuedConnection)
                self.load_models()
                return
        except Exception:
            pass

        QMetaObject.invokeMethod(self, "_set_status_launch", Qt.QueuedConnection)
        try:
            kwargs = {}
            if os.name == 'nt':
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            else:
                kwargs["start_new_session"] = True
            subprocess.Popen(["ollama", "serve"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)

            for _ in range(20):
                time.sleep(0.5)
                try:
                    resp = requests.get(f"{self.ollama_url}/api/tags", timeout=1)
                    if resp.status_code == 200:
                        QMetaObject.invokeMethod(self, "_set_status_started", Qt.QueuedConnection)
                        self.load_models()
                        return
                except Exception:
                    pass
            QMetaObject.invokeMethod(self, "_set_status_fail", Qt.QueuedConnection)
        except Exception:
            QMetaObject.invokeMethod(self, "_set_status_error", Qt.QueuedConnection)

    @Slot()
    def _set_status_ok(self): self.status_text.setText(self.T["status_ollama_ok"])
    @Slot()
    def _set_status_launch(self): self.status_text.setText(self.T["status_launch"])
    @Slot()
    def _set_status_started(self): self.status_text.setText(self.T["status_ollama_started"])
    @Slot()
    def _set_status_fail(self): self.status_text.setText(self.T["status_ollama_fail"])
    @Slot()
    def _set_status_error(self): self.status_text.setText(self.T["status_ollama_error"])

    # ============================================================
    # МОДЕЛИ
    # ============================================================

    def load_models(self):
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            if not models:
                models = ["llama3.2:3b"]
        except Exception:
            models = ["llama3.2:3b"]
        self.models = models
        self.sig_update_model_combo.emit(models)

    @Slot(list)
    def _do_update_model_combo(self, models):
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        self.model_combo.addItems(models)
        if self.model in models:
            self.model_combo.setCurrentText(self.model)
        else:
            self.model_combo.setCurrentIndex(0)
            self.model = models[0]
            self.settings["model"] = self.model
            self.save_settings()
        self.model_combo.blockSignals(False)

    @Slot(object, str)
    def _do_update_bubble(self, bubble, text):
        try:
            bubble.set_text(text)
        except RuntimeError:
            pass

    @Slot()
    def _do_scroll(self):
        sb = self.chat_scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ============================================================
    # ЯЗЫК
    # ============================================================

    def toggle_language(self):
        self.lang = "en" if self.lang == "ru" else "ru"
        self.T = LANGUAGES[self.lang]
        self.settings["lang"] = self.lang
        self.save_settings()
        self.update_ui_texts()

    def update_ui_texts(self):
        self.setWindowTitle(self.T["title"])
        self.panel_title.setText(self.T["settings"])
        self.toggle_btn.setText(self.T["hide"] if self.sidebar_visible else self.T["show"])
        self.theme_label.setText(self.T["theme"])
        self.style_label.setText(self.T["style"])
        self.model_label.setText(self.T["model"])
        self.refresh_btn.setText(self.T["refresh"])
        self.stream_label.setText(self.T["stream"])
        self.stream_checkbox.setText(self.T["stream_check"])
        self.char_label.setText(self.T["character"])
        self.char_btn.setText(self.T["create_character"])
        self.clear_btn.setText(self.T["clear"])
        self.input_field.setPlaceholderText(self.T["send_placeholder"])
        self.lang_btn.setText("Русский" if self.lang == "ru" else "English")
        self.msg_count_label.setText(self.T["msg_count"].format(count=self.msg_counter))

    # ============================================================
    # МЕНЮ ТЕМ / СТИЛЕЙ
    # ============================================================

    def create_theme_menu(self):
        menu = QMenu(self)
        dark = QMenu("🌙 Тёмные", menu)
        for t in sorted([k for k in PALETTES if not PALETTES[k]["light"]]):
            a = dark.addAction(t)
            a.triggered.connect(lambda checked=False, x=t: self.apply_theme(x))
        menu.addMenu(dark)
        light = QMenu("☀️ Светлые", menu)
        for t in sorted([k for k in PALETTES if PALETTES[k]["light"]]):
            a = light.addAction(t)
            a.triggered.connect(lambda checked=False, x=t: self.apply_theme(x))
        menu.addMenu(light)
        return menu

    def show_theme_menu(self):
        m = self.create_theme_menu()
        m.exec_(self.theme_btn.mapToGlobal(self.theme_btn.rect().bottomLeft()))

    def apply_theme(self, theme_name):
        if theme_name == self.current_theme:
            return
        self.current_theme = theme_name
        self.settings["theme"] = theme_name
        self.save_settings()
        self._apply_qss_smooth()

    def create_style_menu(self):
        menu = QMenu(self)
        for s in STYLES.keys():
            a = menu.addAction(s)
            a.triggered.connect(lambda checked=False, x=s: self.apply_style(x))
        return menu

    def show_style_menu(self):
        m = self.create_style_menu()
        m.exec_(self.style_btn.mapToGlobal(self.style_btn.rect().bottomLeft()))

    def apply_style(self, style_name):
        if style_name == self.current_style:
            return
        self.current_style = style_name
        self.settings["style"] = style_name
        self.save_settings()
        self._apply_qss_smooth()

    # ============================================================
    # UI
    # ============================================================

    def _sep(self):
        s = QLabel()
        s.setObjectName("separator")
        s.setFixedHeight(1)
        return s

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        ml = QHBoxLayout(central)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(self.sidebar_width)

        sl = QVBoxLayout(self.sidebar)
        sl.setContentsMargins(18, 20, 18, 20)
        sl.setSpacing(10)

        row = QHBoxLayout(); row.setSpacing(8)
        self.panel_title = QLabel(self.T["settings"])
        self.panel_title.setObjectName("panel_title")
        row.addWidget(self.panel_title)
        row.addStretch()
        self.toggle_btn = QPushButton(self.T["hide"])
        self.toggle_btn.setFixedWidth(80)
        self.toggle_btn.setMinimumHeight(36)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        row.addWidget(self.toggle_btn)
        sl.addLayout(row)

        sl.addWidget(self._sep())

        self.theme_label = QLabel(self.T["theme"]); self.theme_label.setObjectName("muted")
        sl.addWidget(self.theme_label)
        self.theme_btn = QPushButton(f"🎯 {self.current_theme}")
        self.theme_btn.clicked.connect(self.show_theme_menu)
        sl.addWidget(self.theme_btn)

        self.style_label = QLabel(self.T["style"]); self.style_label.setObjectName("muted")
        sl.addWidget(self.style_label)
        self.style_btn = QPushButton(f"🎨 {self.current_style}")
        self.style_btn.clicked.connect(self.show_style_menu)
        sl.addWidget(self.style_btn)

        sl.addWidget(self._sep())

        self.model_label = QLabel(self.T["model"]); self.model_label.setObjectName("muted")
        sl.addWidget(self.model_label)
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.change_model)
        sl.addWidget(self.model_combo)
        self.refresh_btn = QPushButton(self.T["refresh"]); self.refresh_btn.setObjectName("refresh_btn")
        self.refresh_btn.clicked.connect(lambda: threading.Thread(target=self.load_models, daemon=True).start())
        sl.addWidget(self.refresh_btn)

        sl.addWidget(self._sep())

        self.lang_label = QLabel("🌐 Язык / Language"); self.lang_label.setObjectName("muted")
        sl.addWidget(self.lang_label)
        self.lang_btn = QPushButton("Русский" if self.lang == "ru" else "English")
        self.lang_btn.clicked.connect(self.toggle_language)
        sl.addWidget(self.lang_btn)

        self.stream_label = QLabel(self.T["stream"]); self.stream_label.setObjectName("muted")
        sl.addWidget(self.stream_label)
        self.stream_checkbox = QCheckBox(self.T["stream_check"])
        self.stream_checkbox.setChecked(self.settings.get("stream_mode", True))
        self.stream_checkbox.stateChanged.connect(self.toggle_stream_mode)
        sl.addWidget(self.stream_checkbox)

        sl.addWidget(self._sep())

        self.char_label = QLabel(self.T["character"]); self.char_label.setObjectName("muted")
        sl.addWidget(self.char_label)
        self.char_btn = QPushButton(self.T["create_character"])
        self.char_btn.clicked.connect(self.open_character)
        self.char_btn.setMinimumHeight(40)
        sl.addWidget(self.char_btn)

        self.char_info = QLabel(""); self.char_info.setObjectName("muted")
        sl.addWidget(self.char_info)
        if self.current_character:
            self.char_info.setText(f"✓ {self.current_character.get('name','')}")

        sl.addStretch()

        self.clear_btn = QPushButton(self.T["clear"])
        self.clear_btn.setObjectName("clear_btn")
        self.clear_btn.clicked.connect(self.clear_history)
        sl.addWidget(self.clear_btn)

        ml.addWidget(self.sidebar)

        main_content = QWidget()
        ml.addWidget(main_content)

        mcl = QVBoxLayout(main_content)
        mcl.setContentsMargins(14, 14, 14, 14)
        mcl.setSpacing(10)

        header = QWidget(); header.setObjectName("card"); header.setFixedHeight(58)
        hl = QHBoxLayout(header); hl.setContentsMargins(28, 10, 28, 10)
        title = QLabel("✦ NeoBrain"); title.setObjectName("title")
        hl.addWidget(title)
        version = QLabel("v7.4"); version.setObjectName("muted")
        hl.addWidget(version)
        hl.addStretch()
        self.status_label = QLabel(f"🎯 {self.current_theme} • 🎨 {self.current_style}")
        self.status_label.setObjectName("muted")
        hl.addWidget(self.status_label)
        self.indicator = QLabel("●"); self.indicator.setObjectName("muted")
        hl.addWidget(self.indicator)
        mcl.addWidget(header)

        chat_widget = QWidget(); chat_widget.setObjectName("card")
        cl = QVBoxLayout(chat_widget); cl.setContentsMargins(14, 14, 14, 14); cl.setSpacing(0)

        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_container = QWidget()
        self.chat_container_layout = QVBoxLayout(self.chat_container)
        self.chat_container_layout.setContentsMargins(6, 6, 6, 6)
        self.chat_container_layout.setSpacing(10)
        self.chat_container_layout.setAlignment(Qt.AlignTop)
        self.chat_scroll_area.setWidget(self.chat_container)
        cl.addWidget(self.chat_scroll_area)
        mcl.addWidget(chat_widget)

        input_card = QWidget(); input_card.setObjectName("card"); input_card.setFixedHeight(72)
        bl = QHBoxLayout(input_card); bl.setContentsMargins(18, 12, 18, 12); bl.setSpacing(12)

        self.input_field = QLineEdit(); self.input_field.setObjectName("input_field")
        self.input_field.setPlaceholderText(self.T["send_placeholder"])
        self.input_field.returnPressed.connect(self.send_message)
        bl.addWidget(self.input_field)

        self.send_btn = QPushButton("➤"); self.send_btn.setObjectName("send_btn")
        self.send_btn.clicked.connect(self.send_message)
        bl.addWidget(self.send_btn)

        self.stop_btn = QPushButton("⏹"); self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setVisible(False)
        self.stop_btn.clicked.connect(self.stop_generation_handler)
        bl.addWidget(self.stop_btn)

        mcl.addWidget(input_card)

        self.sidebar_trigger_btn = QPushButton("▶")
        self.sidebar_trigger_btn.setObjectName("sidebar_trigger")
        self.sidebar_trigger_btn.setFixedSize(24, 52)
        self.sidebar_trigger_btn.setVisible(False)
        self.sidebar_trigger_btn.setParent(self)
        self.sidebar_trigger_btn.clicked.connect(self.toggle_sidebar)

        sb = QStatusBar(); self.setStatusBar(sb)
        self.status_text = QLabel(self.T["status_checking"])
        sb.addWidget(self.status_text)
        sb.addPermanentWidget(QLabel("|"))
        self.msg_count_label = QLabel(self.T["msg_count"].format(count=self.msg_counter))
        sb.addPermanentWidget(self.msg_count_label)
        self.typing_label = QLabel("")
        sb.addPermanentWidget(self.typing_label)

    # ============================================================
    # SIDEBAR
    # ============================================================

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        target = self.sidebar_width if self.sidebar_visible else 0

        a1 = QPropertyAnimation(self.sidebar, b"minimumWidth")
        a1.setDuration(300); a1.setStartValue(self.sidebar.minimumWidth())
        a1.setEndValue(target); a1.setEasingCurve(QEasingCurve.InOutQuad); a1.start()
        self.sidebar_anim = a1

        a2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
        a2.setDuration(300); a2.setStartValue(self.sidebar.maximumWidth())
        a2.setEndValue(target); a2.setEasingCurve(QEasingCurve.InOutQuad); a2.start()
        self.sidebar_max_anim = a2

        if self.sidebar_visible:
            self.sidebar_trigger_btn.setVisible(False)
            self.toggle_btn.setText(self.T["hide"])
        else:
            self.toggle_btn.setText(self.T["show"])
            self.sidebar_trigger_btn.setVisible(True)
            self.sidebar_trigger_btn.move(0, self.height() // 2 - 26)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.sidebar_visible:
            self.sidebar_trigger_btn.move(0, self.height() // 2 - 26)
        if self._overlay is not None:
            self._overlay.resize(self.size())

    def toggle_stream_mode(self):
        self.settings["stream_mode"] = self.stream_checkbox.isChecked()
        self.save_settings()

    def stop_generation_handler(self):
        self.stop_generation = True
        self.is_generating = False
        self.send_btn.setVisible(True)
        self.send_btn.setEnabled(True)
        self.stop_btn.setVisible(False)
        self.typing_label.setText("⏹ Остановлено")

    # ============================================================
    # ЧАТ
    # ============================================================

    def add_system_message(self, sender, text):
        self.add_message(sender, text, is_system=True)

    def add_message(self, sender, text, restore=False, is_system=False):
        if not restore:
            self.message_history.append({"sender": sender, "text": text})
            self.msg_counter += 1
            self.msg_count_label.setText(self.T["msg_count"].format(count=self.msg_counter))
            self.save_history()

        is_user = (sender not in ("NeoBrain", "✦ NeoBrain"))

        if is_system:
            show_sender = False
            display_name = ""
        else:
            show_sender = True
            display_name = "Вы" if is_user else "NeoBrain"

        bubble = MessageBubble(text, is_user=is_user, sender=display_name,
                                palette_key=self.current_theme,
                                style_key=self.current_style,
                                show_sender=show_sender)
        self.chat_container_layout.addWidget(bubble)
        QTimer.singleShot(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        sb = self.chat_scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    def clear_history(self):
        if QMessageBox.question(self, self.T["clear_confirm"], self.T["clear_confirm_text"],
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        while self.chat_container_layout.count():
            child = self.chat_container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.msg_counter = 0
        self.message_history = []
        self.msg_count_label.setText(self.T["msg_count"].format(count=0))
        self.add_system_message("✦ NeoBrain", self.T["chat_cleared"])
        self.save_settings()

    def change_model(self, text):
        if not text or text == self.model:
            return
        self.model = text
        self.settings["model"] = text
        self.save_settings()

    # ============================================================
    # ПЕРСОНАЖ
    # ============================================================

    def open_character(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.T["character_title"])
        dialog.setFixedSize(520, 600)
        dialog.setStyleSheet(build_qss(self.current_theme, self.current_style))

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)

        t = QLabel(self.T["character_title"]); t.setObjectName("title")
        layout.addWidget(t)

        layout.addWidget(QLabel(self.T["character_name"]))
        name_entry = QLineEdit(); name_entry.setMinimumHeight(42)
        layout.addWidget(name_entry)

        layout.addWidget(QLabel(self.T["character_gender"]))

        ggroup = QButtonGroup(dialog)
        ggroup.setExclusive(True)

        gl = QHBoxLayout(); gl.setSpacing(14)

        male = QPushButton(self.T["character_male"])
        male.setCheckable(True); male.setChecked(True); male.setFixedHeight(46)
        ggroup.addButton(male, 0)
        gl.addWidget(male)

        female = QPushButton(self.T["character_female"])
        female.setCheckable(True); female.setFixedHeight(46)
        ggroup.addButton(female, 1)
        gl.addWidget(female)

        gl.addStretch()
        layout.addLayout(gl)

        # Подсказка о выбранном поле
        gender_hint = QLabel()
        gender_hint.setObjectName("muted")
        gender_hint.setWordWrap(True)
        layout.addWidget(gender_hint)

        def update_hint():
            if ggroup.checkedId() == 0:
                gender_hint.setText("✓ Выбран: ♂ Мужской — персонаж будет говорить «я сделал», «я понял»")
            else:
                gender_hint.setText("✓ Выбран: ♀ Женский — персонаж будет говорить «я сделала», «я поняла»")

        ggroup.idToggled.connect(lambda _id, checked: update_hint() if checked else None)
        update_hint()

        layout.addWidget(QLabel(self.T["character_personality"]))
        p_entry = QLineEdit(); p_entry.setMinimumHeight(42)
        layout.addWidget(p_entry)

        layout.addWidget(QLabel(self.T["character_desc"]))
        d_entry = QTextEdit(); d_entry.setMinimumHeight(70)
        layout.addWidget(d_entry)

        layout.addStretch()
        bl = QHBoxLayout()
        save = QPushButton(self.T["character_create"])
        save.clicked.connect(lambda: self.save_character(name_entry, ggroup, p_entry, d_entry, dialog))
        bl.addWidget(save)
        cancel = QPushButton(self.T["character_cancel"])
        cancel.clicked.connect(dialog.reject)
        bl.addWidget(cancel)
        layout.addLayout(bl)
        dialog.exec_()

    def save_character(self, name_entry, gender_group, personality_entry, desc_entry, dialog):
        name = name_entry.text().strip()
        if not name:
            QMessageBox.warning(self, self.T["character_error"], self.T["character_error_name"])
            return

        gender = "мужской" if gender_group.checkedId() == 0 else "женский"
        pronoun = "он" if gender == "мужской" else "она"
        personality = personality_entry.text().strip()
        desc = desc_entry.toPlainText().strip()

        prompt = f"Ты персонаж по имени {name}."
        if gender == "мужской":
            prompt += " Ты мужчина."
            prompt += " Когда говоришь о себе в прошедшем времени — используй мужской род: 'я сделал', 'я понял', 'я пошёл', 'я сказал'."
            prompt += " Не используй женские формы: 'сделала', 'поняла', 'пошла', 'сказала' — это ошибка."
        else:
            prompt += " Ты женщина."
            prompt += " Когда говоришь о себе в прошедшем времени — используй женский род: 'я сделала', 'я поняла', 'я пошла', 'я сказала'."
            prompt += " Не используй мужские формы: 'сделал', 'понял', 'пошёл', 'сказал' — это ошибка."
        if personality:
            prompt += f" Твой характер: {personality}."
        if desc:
            prompt += f" {desc}"
        prompt += " Всегда оставайся в образе этого персонажа. Говори от первого лица."

        self.current_character = {
            "name": name,
            "gender": gender,
            "personality": personality,
            "description": desc,
            "prompt": prompt,
            "pronoun": pronoun,
        }
        self.settings["current_character"] = self.current_character
        self.settings["characters"][name] = self.current_character
        self.save_settings()

        self.char_info.setText(f"✓ {name} ({gender})")
        self.add_system_message("✦ NeoBrain", self.T["character_created"].format(name=name, gender=gender))
        dialog.accept()

    # ============================================================
    # ОТПРАВКА
    # ============================================================

    def send_message(self):
        text = self.input_field.text().strip()
        if not text or self.is_generating:
            return
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.is_generating = True
        self.stop_generation = False
        self.send_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        self.typing_label.setText(self.T["status_typing"])
        self.add_message("Вы", text)

        ai_bubble = MessageBubble("", is_user=False, sender="NeoBrain",
                                   palette_key=self.current_theme,
                                   style_key=self.current_style)
        self.chat_container_layout.addWidget(ai_bubble)
        self.scroll_to_bottom()

        threading.Thread(target=self.stream_response, args=(text, ai_bubble), daemon=True).start()

    def stream_response(self, user_text, ai_bubble):
        system_prompt = THEME_PROMPTS.get(self.current_theme, "")
        max_tokens = self.settings.get("max_tokens", 512)
        if self.current_character:
            system_prompt += "\n" + self.current_character.get("prompt", "")

        full_prompt = ""
        if system_prompt:
            full_prompt += f"System: {system_prompt}\n"
        for msg in self.message_history[-10:]:
            if msg["sender"] in ("NeoBrain", "✦ NeoBrain"):
                full_prompt += f"Assistant: {msg['text']}\n"
            else:
                full_prompt += f"User: {msg['text']}\n"
        full_prompt += f"User: {user_text}\nAssistant:"

        payload = {"model": self.model, "prompt": full_prompt, "stream": True,
                   "options": {"temperature": self.temperature, "num_predict": max_tokens}}
        stream_mode = self.settings.get("stream_mode", True)
        response_text = ""

        try:
            with requests.post(f"{self.ollama_url}/api/generate", json=payload,
                               stream=True, timeout=60) as r:
                if r.status_code == 200:
                    if stream_mode:
                        for line in r.iter_lines():
                            if self.stop_generation: break
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    chunk = data.get('response', '')
                                    if chunk:
                                        response_text += chunk
                                        self.sig_update_bubble.emit(ai_bubble, response_text)
                                        self.sig_scroll.emit()
                                        time.sleep(0.01)
                                except json.JSONDecodeError:
                                    continue
                    else:
                        for line in r.iter_lines():
                            if self.stop_generation: break
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    chunk = data.get('response', '')
                                    if chunk: response_text += chunk
                                except json.JSONDecodeError:
                                    continue
                        if not self.stop_generation:
                            self.sig_update_bubble.emit(ai_bubble, response_text)
                            self.sig_scroll.emit()
                else:
                    self.sig_update_bubble.emit(ai_bubble, f"⚠️ Ошибка API: {r.status_code}")
            if self.stop_generation:
                self.sig_update_bubble.emit(ai_bubble, response_text + "\n\n⏹ Остановлено")
        except requests.exceptions.ConnectionError:
            self.sig_update_bubble.emit(ai_bubble, "❌ Не удалось подключиться к Ollama.\nЗапусти: `ollama serve`")
        except requests.exceptions.Timeout:
            self.sig_update_bubble.emit(ai_bubble, "⏰ Таймаут.")
        except Exception as e:
            self.sig_update_bubble.emit(ai_bubble, f"❌ Ошибка: {str(e)}")
        finally:
            self.message_history.append({"sender": "NeoBrain", "text": response_text})
            self.save_history()
            QMetaObject.invokeMethod(self, "_finish_generation", Qt.QueuedConnection)

    @Slot()
    def _finish_generation(self):
        self.is_generating = False
        self.input_field.setEnabled(True)
        self.send_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        if not self.stop_generation:
            self.typing_label.setText("")
        else:
            self.typing_label.setText("⏹ Остановлено")
            QTimer.singleShot(2000, lambda: self.typing_label.setText(""))
        self.stop_generation = False
        self.msg_counter += 1
        self.msg_count_label.setText(self.T["msg_count"].format(count=self.msg_counter))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = NeoBrainChat()
    window.show()
    sys.exit(app.exec_())