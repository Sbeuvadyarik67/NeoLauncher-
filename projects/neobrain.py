import sys
import json
import os
import threading
import random
import math
import requests
import subprocess
import time
import shutil
from pathlib import Path
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
        "edit_avatar": "✏ Изменить аватар", "edit_character": "✏ Редактировать персонажа",
        "clear": "🗑 Очистить чат", "send_placeholder": "Напишите сообщение… (Enter для отправки)",
        "status_ready": "Готов", "status_checking": "⏳ Проверка Ollama...",
        "status_ollama_ok": "✅ Ollama запущен", "status_ollama_error": "⚠️ Ollama не доступен",
        "status_launch": "⏳ Запуск Ollama...", "status_ollama_fail": "⚠️ Не удалось запустить Ollama",
        "status_ollama_started": "✅ Ollama запущен", "status_typing": "💬 Печатает...",
        "status_error": "❌ Ошибка: {e}",
        "character_title": "✦ Создать персонажа",
        "character_edit_title": "✏ Редактировать персонажа",
        "character_name": "👤 Имя персонажа:",
        "character_gender": "⚧ Пол:", "character_male": "♂ Мужской", "character_female": "♀ Женский",
        "character_personality": "🧠 Характер (личность):",
        "character_desc": "📝 Описание (как отвечает, стиль речи, манера):",
        "character_create": "✅ Создать", "character_save": "✅ Сохранить",
        "character_cancel": "Отмена",
        "character_error": "Ошибка", "character_error_name": "Введите имя персонажа!",
        "character_error_exists": "Персонаж с именем «{name}» уже существует!",
        "character_created": "✅ Создан персонаж: {name} ({gender})",
        "character_updated": "✅ Персонаж «{name}» обновлён",
        "character_renamed": "✅ Персонаж переименован: «{old}» → «{new}»",
        "msg_count": "Сообщений: {count}", "clear_confirm": "Очистка",
        "clear_confirm_text": "Удалить всю историю чата?", "chat_cleared": "Чат очищен.",
        "model_changed": "Модель изменена на: {model}",
        "theme_changed": "Тема: {theme}", "style_changed": "Стиль: {style}",
        "welcome": "Привет! Я твой AI-помощник. Начни диалог или выбери тему.",
        "avatar_upload": "📁 Загрузить аватар", "avatar_reset": "🗑 Сбросить",
        "avatar_hint": "Аватар (необязательно)",
        "avatar_editor_title": "✏ Настройка аватара",
        "avatar_editor_hint": "Перетащи мышью · Колесо мыши — зум",
        "avatar_zoom": "🔍 Масштаб",
        "avatar_done": "✅ Готово", "avatar_cancel": "Отмена", "avatar_reset_pos": "↺ Сброс",
        "avatar_load_first": "Сначала загрузите аватар",
        "background_section": "🌈 Фон",
        "background_label": "Анимированный фон:",
        "background_none": "— Без фона —",
        "bg_neon": "🌆 Neon",
        "bg_aurora": "🌌 Aurora",
        "bg_sunset": "🌅 Sunset",
        "bg_matrix": "💚 Matrix",
        "bg_sakura": "🌸 Sakura",
        "bg_ocean": "🌊 Deep Ocean",
        "bg_ember": "🔥 Ember",
        "background_speed": "⚡ Скорость:",
        "background_particles": "✨ Частицы",
        "background_animate": "🎬 Анимация",
        "background_translucent": "🔮 Прозрачные панели",
        "bg_changed": "🌈 Фон: {name}",
    },
    "en": {
        "title": "✦ NeoBrain", "settings": "✦ Settings", "hide": "◀ Hide", "show": "▶ Show",
        "theme": "🎯 Theme", "style": "🎨 Style", "style_default": "Default",
        "model": "🧠 Model", "refresh": "🔄 Refresh models",
        "stream": "💬 Stream mode", "stream_check": "Enable smooth output",
        "character": "👤 Character", "create_character": "➕ Create character",
        "edit_avatar": "✏ Edit avatar", "edit_character": "✏ Edit character",
        "clear": "🗑 Clear chat", "send_placeholder": "Type a message… (Enter to send)",
        "status_ready": "Ready", "status_checking": "⏳ Checking Ollama...",
        "status_ollama_ok": "✅ Ollama running", "status_ollama_error": "⚠️ Ollama unavailable",
        "status_launch": "⏳ Starting Ollama...", "status_ollama_fail": "⚠️ Failed to start Ollama",
        "status_ollama_started": "✅ Ollama started", "status_typing": "💬 Typing...",
        "status_error": "❌ Error: {e}",
        "character_title": "✦ Create character",
        "character_edit_title": "✏ Edit character",
        "character_name": "👤 Character name:",
        "character_gender": "⚧ Gender:", "character_male": "♂ Male", "character_female": "♀ Female",
        "character_personality": "🧠 Personality:",
        "character_desc": "📝 Description (style, manner):",
        "character_create": "✅ Create", "character_save": "✅ Save",
        "character_cancel": "Cancel",
        "character_error": "Error", "character_error_name": "Enter character name!",
        "character_error_exists": "Character «{name}» already exists!",
        "character_created": "✅ Character created: {name} ({gender})",
        "character_updated": "✅ Character «{name}» updated",
        "character_renamed": "✅ Character renamed: «{old}» → «{new}»",
        "msg_count": "Messages: {count}", "clear_confirm": "Clear",
        "clear_confirm_text": "Delete entire chat history?", "chat_cleared": "Chat cleared.",
        "model_changed": "Model changed to: {model}",
        "theme_changed": "Theme: {theme}", "style_changed": "Style: {style}",
        "welcome": "Hi! I'm your AI assistant. Start a conversation or choose a theme.",
        "avatar_upload": "📁 Upload avatar", "avatar_reset": "🗑 Reset",
        "avatar_hint": "Avatar (optional)",
        "avatar_editor_title": "✏ Avatar editor",
        "avatar_editor_hint": "Drag with mouse · Wheel to zoom",
        "avatar_zoom": "🔍 Zoom",
        "avatar_done": "✅ Done", "avatar_cancel": "Cancel", "avatar_reset_pos": "↺ Reset",
        "avatar_load_first": "Load an avatar first",
        "background_section": "🌈 Background",
        "background_label": "Animated background:",
        "background_none": "— No background —",
        "bg_neon": "🌆 Neon",
        "bg_aurora": "🌌 Aurora",
        "bg_sunset": "🌅 Sunset",
        "bg_matrix": "💚 Matrix",
        "bg_sakura": "🌸 Sakura",
        "bg_ocean": "🌊 Deep Ocean",
        "bg_ember": "🔥 Ember",
        "background_speed": "⚡ Speed:",
        "background_particles": "✨ Particles",
        "background_animate": "🎬 Animation",
        "background_translucent": "🔮 Translucent panels",
        "bg_changed": "🌈 Background: {name}",
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


# ======================================================
# АВАТАРЫ
# ======================================================

AVATARS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NeoBrain", "avatars")
USER_AVATAR_DIR = os.path.join(AVATARS_DIR, "user")

os.makedirs(AVATARS_DIR, exist_ok=True)
os.makedirs(USER_AVATAR_DIR, exist_ok=True)


def _safe_name(name: str) -> str:
    if not name:
        return ""
    return "".join(c for c in name if c.isalnum() or c in "-_ ").strip()


def get_avatar_path(character_name: str):
    if not character_name:
        return None
    safe = _safe_name(character_name)
    if not safe:
        return None
    folder = os.path.join(AVATARS_DIR, safe)
    for ext in ("png", "jpg", "jpeg", "webp"):
        path = os.path.join(folder, f"avatar.{ext}")
        if os.path.exists(path):
            return path
    return None


def save_avatar(character_name: str, src_path: str):
    if not character_name or not src_path or not os.path.exists(src_path):
        return None
    safe = _safe_name(character_name)
    if not safe:
        return None
    folder = os.path.join(AVATARS_DIR, safe)
    os.makedirs(folder, exist_ok=True)
    for old_ext in ("png", "jpg", "jpeg", "webp"):
        old = os.path.join(folder, f"avatar.{old_ext}")
        if os.path.exists(old):
            try:
                os.remove(old)
            except OSError:
                pass
    ext = os.path.splitext(src_path)[1].lower().lstrip(".") or "png"
    if ext == "jpeg":
        ext = "jpg"
    if ext not in ("png", "jpg", "webp"):
        ext = "png"
    dst = os.path.join(folder, f"avatar.{ext}")
    try:
        shutil.copy2(src_path, dst)
        return dst
    except OSError:
        return None


def delete_avatar(character_name: str) -> bool:
    if not character_name:
        return False
    safe = _safe_name(character_name)
    folder = os.path.join(AVATARS_DIR, safe)
    if not os.path.isdir(folder):
        return False
    removed = False
    for ext in ("png", "jpg", "jpeg", "webp"):
        path = os.path.join(folder, f"avatar.{ext}")
        if os.path.exists(path):
            try:
                os.remove(path)
                removed = True
            except OSError:
                pass
    return removed


def rename_avatar_folder(old_name: str, new_name: str) -> bool:
    if not old_name or not new_name or old_name == new_name:
        return False
    old_safe = _safe_name(old_name)
    new_safe = _safe_name(new_name)
    if not old_safe or not new_safe or old_safe == new_safe:
        return False
    old_folder = os.path.join(AVATARS_DIR, old_safe)
    new_folder = os.path.join(AVATARS_DIR, new_safe)
    if not os.path.isdir(old_folder):
        return False
    try:
        if os.path.isdir(new_folder):
            for f in os.listdir(old_folder):
                shutil.copy2(os.path.join(old_folder, f), os.path.join(new_folder, f))
            shutil.rmtree(old_folder, ignore_errors=True)
        else:
            os.rename(old_folder, new_folder)
        return True
    except OSError:
        return False


def make_round_pixmap(pixmap: QPixmap, size: int,
                       zoom: float = 1.0,
                       offset_x: float = 0.0,
                       offset_y: float = 0.0,
                       dim_outside: bool = False,
                       dim_alpha: float = 0.40) -> QPixmap:
    if pixmap.isNull():
        return pixmap

    zoom = max(0.1, float(zoom))
    target = max(1, int(round(size * zoom)))

    scaled = pixmap.scaled(
        target, target,
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation
    )

    out = QPixmap(size, size)
    out.fill(Qt.transparent)
    painter = QPainter(out)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)

    px_offset_x = int(offset_x * size)
    px_offset_y = int(offset_y * size)

    draw_x = (size - scaled.width()) // 2 + px_offset_x
    draw_y = (size - scaled.height()) // 2 + px_offset_y
    painter.drawPixmap(draw_x, draw_y, scaled)

    if dim_outside:
        painter.setClipping(False)
        outer = QPainterPath()
        outer.addRect(0, 0, size, size)
        inner = QPainterPath()
        inner.addEllipse(0, 0, size, size)
        mask = outer.subtracted(inner)
        painter.fillPath(mask, QColor(0, 0, 0, int(255 * max(0.0, min(1.0, dim_alpha)))))

    painter.end()
    return out


def make_letter_avatar(name: str, size: int, accent_hex: str = "#8b5cf6",
                        accent2_hex: str = "#00d4ff") -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0.0, QColor(accent_hex))
    grad.setColorAt(1.0, QColor(accent2_hex))
    painter.setBrush(QBrush(grad))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, size, size)
    letter = (name.strip()[0] if name.strip() else "?").upper()
    font = QFont()
    font.setPointSize(int(size * 0.45))
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor("white"))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, letter)
    painter.end()
    return pixmap


def get_character_pixmap(character_name: str, size: int,
                          palette_key: str = "🌆 Неон",
                          style_key: str = "По умолчанию",
                          character: dict = None,
                          zoom: float = None,
                          offset_x: float = None,
                          offset_y: float = None) -> QPixmap:
    p = get_effective_palette(palette_key, style_key)
    accent = QColor(p["accent"]).name()
    accent2 = QColor(p["accent2"]).name()

    if character:
        if zoom is None:
            zoom = float(character.get("avatar_zoom", 1.0))
        if offset_x is None:
            offset_x = float(character.get("avatar_offset_x", 0.0))
        if offset_y is None:
            offset_y = float(character.get("avatar_offset_y", 0.0))

    if zoom is None: zoom = 1.0
    if offset_x is None: offset_x = 0.0
    if offset_y is None: offset_y = 0.0

    path = get_avatar_path(character_name)
    if path:
        pm = QPixmap(path)
        if not pm.isNull():
            return make_round_pixmap(pm, size, zoom, offset_x, offset_y)
    return make_letter_avatar(character_name or "?", size, accent, accent2)


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
QSlider::groove:horizontal {{
    background: {p['input_border']};
    height: 6px;
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {p['accent']};
    width: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}
QSlider::handle:horizontal:hover {{
    background: {p['accent2']};
}}
"""

# ======================================================
# АНИМИРОВАННЫЕ ФОНЫ
# ======================================================

BACKGROUNDS = {
    "neon": {
        "name": "🌆 Neon",
        "colors": [QColor("#0a0512"), QColor("#1a0a2e"), QColor("#0a1a2a")],
        "particle": "spark",
        "particle_color": QColor("#ff2d8a"),
        "particle_color2": QColor("#00d4ff"),
    },
    "aurora": {
        "name": "🌌 Aurora",
        "colors": [QColor("#0a1420"), QColor("#0d2233"), QColor("#102a3a")],
        "particle": "snow",
        "particle_color": QColor("#a5f3fc"),
        "particle_color2": QColor("#67e8f9"),
    },
    "sunset": {
        "name": "🌅 Sunset",
        "colors": [QColor("#1a0a1e"), QColor("#2a0a24"), QColor("#1a0a1e")],
        "particle": "dust",
        "particle_color": QColor("#fbbf24"),
        "particle_color2": QColor("#ff7b72"),
    },
    "matrix": {
        "name": "💚 Matrix",
        "colors": [QColor("#000000"), QColor("#001a08"), QColor("#000000")],
        "particle": "code",
        "particle_color": QColor("#22c55e"),
        "particle_color2": QColor("#10b981"),
    },
    "sakura": {
        "name": "🌸 Sakura",
        "colors": [QColor("#1a0a1e"), QColor("#2a1024"), QColor("#1a0a1e")],
        "particle": "petal",
        "particle_color": QColor("#f9a8d4"),
        "particle_color2": QColor("#c084fc"),
    },
    "ocean": {
        "name": "🌊 Deep Ocean",
        "colors": [QColor("#020617"), QColor("#0c4a6e"), QColor("#082f49")],
        "particle": "bubble",
        "particle_color": QColor("#0ea5e9"),
        "particle_color2": QColor("#06b6d4"),
    },
    "ember": {
        "name": "🔥 Ember",
        "colors": [QColor("#1a0a05"), QColor("#2a0a08"), QColor("#1a0505")],
        "particle": "spark",
        "particle_color": QColor("#ff6b35"),
        "particle_color2": QColor("#ffd93d"),
    },
}


class Particle:
    """Одна частица для анимированного фона."""

    def __init__(self, w, h, kind, color, color2):
        self.w = w
        self.h = h
        self.kind = kind
        self.color = color
        self.color2 = color2
        self.reset(initial=True)

    def reset(self, initial=False):
        w, h = self.w, self.h
        self.alpha = random.uniform(0.3, 1.0)
        if self.kind == "spark":
            self.x = random.uniform(0, w)
            self.y = h + random.uniform(0, h) if initial else h + 10
            self.vx = random.uniform(-15, 15)
            self.vy = random.uniform(-60, -20)
            self.size = random.uniform(1.5, 3.5)
        elif self.kind == "snow":
            self.x = random.uniform(0, w)
            self.y = random.uniform(-h, 0) if initial else -10
            self.vx = random.uniform(-20, 20)
            self.vy = random.uniform(20, 60)
            self.size = random.uniform(1.5, 3)
        elif self.kind == "dust":
            self.x = random.uniform(0, w)
            self.y = random.uniform(0, h)
            self.vx = random.uniform(-25, 25)
            self.vy = random.uniform(-15, 15)
            self.size = random.uniform(1, 2.5)
        elif self.kind == "code":
            self.x = random.uniform(0, w)
            self.y = random.uniform(-h, 0) if initial else -20
            self.vx = 0
            self.vy = random.uniform(80, 180)
            self.size = random.uniform(10, 16)
        elif self.kind == "petal":
            self.x = random.uniform(0, w)
            self.y = random.uniform(-h, 0) if initial else -10
            self.vx = random.uniform(-30, 30)
            self.vy = random.uniform(15, 40)
            self.size = random.uniform(3, 6)
            self.phase = random.uniform(0, math.tau)
        elif self.kind == "bubble":
            self.x = random.uniform(0, w)
            self.y = h + random.uniform(0, h) if initial else h + 10
            self.vx = random.uniform(-10, 10)
            self.vy = random.uniform(-40, -15)
            self.size = random.uniform(2, 5)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.kind == "petal":
            self.phase = getattr(self, "phase", 0) + dt * 3
            self.x += math.sin(self.phase) * 15 * dt
        if self.kind in ("spark", "bubble"):
            if self.y < -20:
                self.reset()
        elif self.kind in ("snow", "code", "petal"):
            if self.y > self.h + 20:
                self.reset()
        elif self.kind == "dust":
            if self.x < -20 or self.x > self.w + 20 or self.y < -20 or self.y > self.h + 20:
                self.reset()


class AnimatedBackground(QWidget):
    """Виджет с анимированным градиентом и частицами."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._bg_id = None
        self._target_bg_id = None
        self._bg_data = None
        self._target_bg_data = None
        self._transition = 1.0

        self._particles = []
        self._particles_enabled = True
        self._animation_enabled = True
        self._time_offset = 0.0
        self._speed = 20.0

        self._timer = QTimer(self)
        self._timer.setInterval(int(1000 / 30))
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        self._last_time = time.time()

    def set_background(self, bg_id: str):
        if bg_id == self._bg_id and self._bg_data is not None:
            return
        if bg_id is None or bg_id not in BACKGROUNDS:
            self._target_bg_id = None
            self._target_bg_data = None
            self._transition = 0.0
            return
        if self._bg_id is None:
            self._bg_id = bg_id
            self._bg_data = BACKGROUNDS[bg_id]
            self._target_bg_id = bg_id
            self._target_bg_data = self._bg_data
            self._transition = 1.0
            self._spawn_particles()
        else:
            self._target_bg_id = bg_id
            self._target_bg_data = BACKGROUNDS[bg_id]
            self._transition = 0.0
            self._spawn_particles_for(self._target_bg_data)

    def set_particles_enabled(self, enabled: bool):
        self._particles_enabled = enabled

    def set_animation_enabled(self, enabled: bool):
        self._animation_enabled = enabled
        if enabled:
            self._last_time = time.time()
            self._timer.start()
        else:
            self._timer.stop()

    def set_speed(self, seconds: float):
        self._speed = max(3.0, float(seconds))

    def _spawn_particles(self):
        if not self._bg_data:
            self._particles = []
            return
        self._spawn_particles_for(self._bg_data)

    def _spawn_particles_for(self, bg_data):
        w = max(1, self.width())
        h = max(1, self.height())
        count = 80
        self._particles = [
            Particle(w, h, bg_data["particle"],
                     bg_data["particle_color"], bg_data["particle_color2"])
            for _ in range(count)
        ]

    def _tick(self):
        now = time.time()
        dt = now - self._last_time
        self._last_time = now
        if dt > 0.1:
            dt = 0.1

        if self._transition < 1.0 and self._target_bg_data is not None:
            self._transition = min(1.0, self._transition + dt / 1.5)
            if self._transition >= 1.0:
                self._bg_id = self._target_bg_id
                self._bg_data = self._target_bg_data

        self._time_offset += dt * (60.0 / self._speed)

        if self._particles_enabled:
            for p in self._particles:
                p.update(dt)

        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._bg_data:
            self._spawn_particles_for(self._bg_data)

    def paintEvent(self, event):
        if self._bg_data is None and self._target_bg_data is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        w = self.width()
        h = self.height()

        if self._transition < 1.0 and self._target_bg_data is not None:
            self._draw_gradient(painter, self._bg_data, w, h, 1.0 - self._transition)
            self._draw_gradient(painter, self._target_bg_data, w, h, self._transition)
        else:
            self._draw_gradient(painter, self._bg_data or self._target_bg_data, w, h, 1.0)

        if self._particles_enabled and self._particles:
            for p in self._particles:
                self._draw_particle(painter, p)

        painter.end()

    def _draw_gradient(self, painter, bg_data, w, h, alpha_factor):
        if not bg_data:
            return
        colors = bg_data["colors"]
        grad = QLinearGradient(0, 0, w, h)
        for i, c in enumerate(colors):
            c2 = QColor(c)
            c2.setAlphaF(alpha_factor)
            grad.setColorAt(i / max(1, len(colors) - 1), c2)
        painter.fillRect(0, 0, w, h, QBrush(grad))

    def _draw_particle(self, painter, p):
        color = p.color
        c = QColor(color)
        alpha = p.alpha
        if p.kind == "spark":
            alpha *= 0.7 + 0.3 * math.sin(self._time_offset * 5 + p.x)
        elif p.kind == "snow":
            alpha *= 0.8 + 0.2 * math.sin(self._time_offset * 2 + p.y * 0.01)
        c.setAlphaF(min(1.0, max(0.0, alpha)))
        painter.setBrush(QBrush(c))
        painter.setPen(Qt.NoPen)

        if p.kind == "code":
            painter.setPen(QPen(c, 1))
            font = QFont("Consolas", int(p.size))
            painter.setFont(font)
            char = random.choice("01")
            painter.drawText(int(p.x), int(p.y), char)
        elif p.kind == "petal":
            painter.save()
            painter.translate(p.x, p.y)
            painter.rotate(math.degrees(self._time_offset * 40 + p.x))
            painter.drawEllipse(QPointF(0, 0), p.size, p.size * 0.5)
            painter.restore()
        else:
            painter.drawEllipse(QPointF(p.x, p.y), p.size, p.size)




# ======================================================
# OVERLAY ДЛЯ ПЛАВНОЙ СМЕНЫ ТЕМЫ
# ======================================================

class FadeOverlay(QWidget):
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
# АВАТАР-ВИДЖЕТ
# ======================================================

class AvatarWidget(QLabel):
    def __init__(self, name: str, size: int = 36,
                 palette_key: str = "🌆 Неон",
                 style_key: str = "По умолчанию",
                 is_user: bool = False,
                 character: dict = None,
                 parent=None):
        super().__init__(parent)
        self.avatar_name = name
        self.avatar_size = size
        self.palette_key = palette_key
        self.style_key = style_key
        self.is_user = is_user
        self.character = character or {}
        self.setFixedSize(size, size)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setScaledContents(False)
        self.setStyleSheet("background: transparent; border: none;")
        self._refresh()

    def _refresh(self):
        if self.is_user:
            pm = make_letter_avatar(self.avatar_name or "Вы", self.avatar_size, "#4facfe", "#8b5cf6")
        else:
            pm = get_character_pixmap(
                self.avatar_name, self.avatar_size,
                self.palette_key, self.style_key,
                character=self.character
            )
        self.setPixmap(pm)

    def update_palette(self, palette_key: str, style_key: str):
        self.palette_key = palette_key
        self.style_key = style_key
        self._refresh()

    def update_name(self, name: str, character: dict = None):
        self.avatar_name = name
        if character is not None:
            self.character = character
        self._refresh()


# ======================================================
# РЕДАКТОР АВАТАРА (drag + zoom)
# ======================================================

class AvatarEditorDialog(QDialog):
    """Мини-редактор: таскаем фото внутри круга, зум колесом/слайдером."""

    CANVAS_SIZE = 260

    def __init__(self, source_pixmap: QPixmap,
                 palette_key: str = "🌆 Неон",
                 style_key: str = "По умолчанию",
                 initial_zoom: float = 1.0,
                 initial_offset_x: float = 0.0,
                 initial_offset_y: float = 0.0,
                 parent=None):
        super().__init__(parent)
        self.setWindowTitle("✏ Настройка аватара")
        self.setFixedSize(420, 500)
        self.setStyleSheet(build_qss(palette_key, style_key))

        self._source = source_pixmap
        self._zoom = initial_zoom
        self._offset_x = initial_offset_x
        self._offset_y = initial_offset_y
        self._dragging = False
        self._drag_start = QPoint()
        self._offset_at_drag = (initial_offset_x, initial_offset_y)
        self._result = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("✏ Настройка аватара")
        title.setObjectName("title")
        layout.addWidget(title)

        hint = QLabel("Перетащи мышью · Колесо мыши — зум")
        hint.setObjectName("muted")
        layout.addWidget(hint)

        self.canvas = QLabel()
        self.canvas.setFixedSize(self.CANVAS_SIZE, self.CANVAS_SIZE)
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setStyleSheet(
            "background: rgba(255,255,255,0.04);"
            "border: 2px dashed rgba(255,255,255,0.18);"
            "border-radius: %dpx;" % (self.CANVAS_SIZE // 2)
        )
        self.canvas.setMouseTracking(True)
        self.canvas.installEventFilter(self)

        canvas_wrap = QHBoxLayout()
        canvas_wrap.addStretch()
        canvas_wrap.addWidget(self.canvas)
        canvas_wrap.addStretch()
        layout.addLayout(canvas_wrap)

        zoom_row = QHBoxLayout()
        zoom_row.setSpacing(10)
        zl = QLabel("🔍 Масштаб"); zl.setObjectName("muted")
        zoom_row.addWidget(zl)

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(50)
        self.zoom_slider.setMaximum(300)
        self.zoom_slider.setValue(int(self._zoom * 100))
        self.zoom_slider.valueChanged.connect(self._on_zoom_slider)
        zoom_row.addWidget(self.zoom_slider, 1)

        self.zoom_value = QLabel(f"{self._zoom:.2f}")
        self.zoom_value.setObjectName("muted")
        self.zoom_value.setFixedWidth(46)
        self.zoom_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        zoom_row.addWidget(self.zoom_value)

        layout.addLayout(zoom_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        reset_btn = QPushButton("↺ Сброс")
        reset_btn.setObjectName("refresh_btn")
        reset_btn.clicked.connect(self._reset)
        btn_row.addWidget(reset_btn)

        btn_row.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("refresh_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        done_btn = QPushButton("✅ Готово")
        done_btn.clicked.connect(self._accept)
        btn_row.addWidget(done_btn)

        layout.addLayout(btn_row)

        self._render()

    def _render(self):
        if self._source.isNull():
            return
        pix = make_round_pixmap(
            self._source, self.CANVAS_SIZE,
            self._zoom, self._offset_x, self._offset_y,
            dim_outside=True,
            dim_alpha=0.40,
        )
        self.canvas.setPixmap(pix)
        self.zoom_value.setText(f"{self._zoom:.2f}")
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(int(self._zoom * 100))
        self.zoom_slider.blockSignals(False)

    def eventFilter(self, obj, event):
        if obj is self.canvas:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self._dragging = True
                self._drag_start = event.position().toPoint()
                self._offset_at_drag = (self._offset_x, self._offset_y)
                return True
            if event.type() == QEvent.MouseMove and self._dragging:
                delta = event.position().toPoint() - self._drag_start
                self._offset_x = self._offset_at_drag[0] - delta.x() / self.CANVAS_SIZE
                self._offset_y = self._offset_at_drag[1] - delta.y() / self.CANVAS_SIZE
                self._render()
                return True
            if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                self._dragging = False
                return True
            if event.type() == QEvent.Wheel:
                step = 0.05
                if event.angleDelta().y() > 0:
                    self._zoom = min(3.0, self._zoom + step)
                else:
                    self._zoom = max(0.5, self._zoom - step)
                self._render()
                return True
        return super().eventFilter(obj, event)

    def _on_zoom_slider(self, value):
        self._zoom = value / 100.0
        self._render()

    def _reset(self):
        self._zoom = 1.0
        self._offset_x = 0.0
        self._offset_y = 0.0
        self._render()

    def _accept(self):
        self._result = (self._zoom, self._offset_x, self._offset_y)
        self.accept()

    def get_result(self):
        return self._result


# ======================================================
# ПУЗЫРЁК СООБЩЕНИЯ
# ======================================================

class MessageBubble(QWidget):
    def __init__(self, text, is_user=False, sender="", palette_key="🌆 Неон",
                 style_key="По умолчанию", show_sender=True,
                 avatar_name: str = "", character: dict = None, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.sender_text = sender
        self.show_sender = show_sender
        self.avatar_name = avatar_name or sender
        self.character = character or {}

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 6, 10, 6)
        main_layout.setSpacing(10)

        self.avatar = AvatarWidget(
            self.avatar_name, size=40,
            palette_key=palette_key, style_key=style_key,
            is_user=is_user,
            character=self.character
        )
        self.avatar.setAlignment(Qt.AlignTop)
        self.avatar.setMinimumSize(40, 40)
        self.avatar.setMaximumSize(40, 40)

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
            main_layout.addWidget(self.avatar)
        else:
            main_layout.addWidget(self.avatar)
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

        if hasattr(self, "avatar"):
            self.avatar.update_palette(palette_key, style_key)

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
        self.msg_counter = 0

        self.sidebar_visible = True
        self.sidebar_width = 270
        self.models = ["llama3.2:3b"]
        self.characters = self.settings.get("characters", {})
        self.current_character = self.settings.get("current_character", None)

        self.is_generating = False
        self.stop_generation = False
        self._theme_animating = False
        self._overlay = None

        self.bg_id = self.settings.get("bg_id", None)
        self.bg_particles = bool(self.settings.get("bg_particles", True))
        self.bg_animate = bool(self.settings.get("bg_animate", True))
        self.bg_translucent = bool(self.settings.get("bg_translucent", False))
        self.bg_speed = float(self.settings.get("bg_speed", 20.0))

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
        self._init_background()

        self.status_text.setText(self.T["status_checking"])
        threading.Thread(target=self._check_ollama_async, daemon=True).start()

        self._reload_chat()

    # ============================================================
    # ФОН
    # ============================================================

    def _init_background(self):
        self.background = AnimatedBackground(self)
        self.background.setGeometry(self.rect())
        self.background.lower()
        self.background.show()

        self.background.set_speed(self.bg_speed)
        self.background.set_particles_enabled(self.bg_particles)
        self.background.set_animation_enabled(self.bg_animate)
        if self.bg_id and self.bg_id in BACKGROUNDS:
            self.background.set_background(self.bg_id)

    def _apply_background(self, bg_id):
        self.bg_id = bg_id if (bg_id and bg_id in BACKGROUNDS) else None
        self.settings["bg_id"] = self.bg_id
        self.save_settings()
        if hasattr(self, "background"):
            self.background.set_background(self.bg_id)
        if hasattr(self, "bg_status_label"):
            name = BACKGROUNDS[self.bg_id]["name"] if self.bg_id else self.T["background_none"]
            self.bg_status_label.setText(name)

    def _toggle_particles(self, state):
        self.bg_particles = bool(state)
        self.settings["bg_particles"] = self.bg_particles
        self.save_settings()
        if hasattr(self, "background"):
            self.background.set_particles_enabled(self.bg_particles)

    def _toggle_animation(self, state):
        self.bg_animate = bool(state)
        self.settings["bg_animate"] = self.bg_animate
        self.save_settings()
        if hasattr(self, "background"):
            self.background.set_animation_enabled(self.bg_animate)

    def _toggle_translucent(self, state):
        self.bg_translucent = bool(state)
        self.settings["bg_translucent"] = self.bg_translucent
        self.save_settings()
        self._apply_qss_now()

    def _on_speed_change(self, value):
        self.bg_speed = float(value)
        self.settings["bg_speed"] = self.bg_speed
        self.save_settings()
        if hasattr(self, "background"):
            self.background.set_speed(self.bg_speed)
        if hasattr(self, "bg_speed_value"):
            self.bg_speed_value.setText(f"{int(value)}s")

    # ============================================================
    # QSS
    # ============================================================

    def _apply_qss_now(self):
        qss = build_qss(self.current_theme, self.current_style)
        if self.bg_translucent:
            p = get_effective_palette(self.current_theme, self.current_style)
            qss = qss.replace(p["card"], "rgba(20,20,30,0.55)")
            qss = qss.replace(p["bg"], "rgba(10,10,20,0.55)")
        self.setStyleSheet("")
        self.setStyleSheet(qss)
        self._refresh_bubbles_palette()
        self.theme_btn.setText(f"🎯 {self.current_theme}")
        self.style_btn.setText(f"🎨 {self.current_style}")
        self.status_label.setText(f"🎯 {self.current_theme} • 🎨 {self.current_style}")
        if hasattr(self, "_update_header_character"):
            self._update_header_character()
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
        if self.bg_translucent:
            p = get_effective_palette(self.current_theme, self.current_style)
            qss = qss.replace(p["card"], "rgba(20,20,30,0.55)")
            qss = qss.replace(p["bg"], "rgba(10,10,20,0.55)")
        self.setStyleSheet("")
        self.setStyleSheet(qss)
        self._refresh_bubbles_palette()
        self.theme_btn.setText(f"🎯 {self.current_theme}")
        self.style_btn.setText(f"🎨 {self.current_style}")
        self.status_label.setText(f"🎯 {self.current_theme} • {self.current_style}")
        if hasattr(self, "_update_header_character"):
            self._update_header_character()
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
            "auto_save": True, "stream_mode": True, "max_tokens": 512, "lang": "ru",
            "bg_id": None, "bg_particles": True, "bg_animate": True,
            "bg_translucent": False, "bg_speed": 20.0,
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
            self.save_settings()

    def _current_history(self):
        if self.current_character:
            name = self.current_character.get("name")
            if name:
                chars = self.settings.setdefault("characters", {})
                char = chars.setdefault(name, {})
                if "history" not in char:
                    char["history"] = []
                return char["history"]
        if "history_no_character" not in self.settings:
            self.settings["history_no_character"] = []
        return self.settings["history_no_character"]

    def _reload_chat(self):
        while self.chat_container_layout.count():
            child = self.chat_container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        history = self._current_history()
        self.msg_counter = len(history)
        if history:
            for msg in history:
                self.add_message(msg.get("sender", "NeoBrain"), msg.get("text", ""), restore=True)
        else:
            self.add_system_message("✦ NeoBrain", self.T["welcome"])
        self.msg_count_label.setText(self.T["msg_count"].format(count=self.msg_counter))

    def on_character_selected(self, index):
        name = self.char_combo.itemData(index)
        if name is None:
            self.current_character = None
            self.settings["current_character"] = None
            self.char_info.setText("")
        else:
            char = self.settings.get("characters", {}).get(name)
            if not char:
                return
            self.current_character = char
            self.settings["current_character"] = char
            self.char_info.setText(f"✓ {name} ({char.get('gender','')})")
        self.save_settings()
        self._update_header_character()
        self._reload_chat()

    def _update_header_character(self):
        if not hasattr(self, "header_avatar"):
            return
        if self.current_character:
            name = self.current_character.get("name", "")
            self.header_avatar.update_name(name, self.current_character)
            self.header_avatar.update_palette(self.current_theme, self.current_style)
            self.header_avatar.setFixedSize(48, 48)
            self.header_avatar.repaint()
            self.header_char_name.setText(name)
            desc = (self.current_character.get("personality")
                    or self.current_character.get("description")
                    or "Персонаж")
            self.header_char_desc.setText(desc[:60] + ("…" if len(desc) > 60 else ""))
        else:
            self.header_avatar.update_name("", {})
            self.header_avatar.update_palette(self.current_theme, self.current_style)
            self.header_char_name.setText("Без персонажа")
            self.header_char_desc.setText("Выберите персонажа в настройках")

    def delete_character(self):
        if not self.current_character:
            QMessageBox.information(self, "Удаление", "Персонаж не выбран.")
            return
        name = self.current_character.get("name")
        if not name:
            return
        answer = QMessageBox.question(
            self, "Удалить персонажа?",
            f"Удалить персонажа «{name}»?\nИстория чата будет потеряна.",
            QMessageBox.Yes | QMessageBox.No)
        if answer != QMessageBox.Yes:
            return
        chars = self.settings.get("characters", {})
        if name in chars:
            del chars[name]
        delete_avatar(name)
        idx = self.char_combo.findData(name)
        if idx >= 0:
            self.char_combo.blockSignals(True)
            self.char_combo.removeItem(idx)
            self.char_combo.setCurrentIndex(0)
            self.char_combo.blockSignals(False)
        self.current_character = None
        self.settings["current_character"] = None
        self.char_info.setText("")
        self.save_settings()
        self._update_header_character()
        self._reload_chat()

    # ============================================================
    # РЕДАКТОР АВАТАРА СУЩЕСТВУЮЩЕГО ПЕРСОНАЖА
    # ============================================================

    def edit_current_avatar(self):
        if not self.current_character:
            QMessageBox.information(self, "Аватар", "Персонаж не выбран.")
            return
        name = self.current_character.get("name")
        if not name:
            return

        path = get_avatar_path(name)
        if not path:
            QMessageBox.information(self, "Аватар",
                                     "У этого персонажа ещё нет аватара.\nЗагрузите изображение.")
            return

        pm = QPixmap(path)
        if pm.isNull():
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить аватар.")
            return

        dlg = AvatarEditorDialog(
            pm,
            palette_key=self.current_theme,
            style_key=self.current_style,
            initial_zoom=float(self.current_character.get("avatar_zoom", 1.0)),
            initial_offset_x=float(self.current_character.get("avatar_offset_x", 0.0)),
            initial_offset_y=float(self.current_character.get("avatar_offset_y", 0.0)),
            parent=self
        )
        if dlg.exec_() == QDialog.Accepted:
            result = dlg.get_result()
            if result:
                zoom, ox, oy = result
                self.current_character["avatar_zoom"] = zoom
                self.current_character["avatar_offset_x"] = ox
                self.current_character["avatar_offset_y"] = oy
                self.settings["characters"][name] = self.current_character
                self.settings["current_character"] = self.current_character
                self.save_settings()
                self._update_header_character()
                self._reload_chat()

    # ============================================================
    # РЕДАКТОР ПЕРСОНАЖА (полная модалка)
    # ============================================================

    def edit_current_character(self):
        if not self.current_character:
            QMessageBox.information(self, "Редактирование", "Персонаж не выбран.")
            return
        self.open_character(character_to_edit=self.current_character)

    def _generate_prompt(self, name, gender, personality, desc):
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
        return prompt

    

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
        self.edit_char_btn.setText(self.T["edit_character"])
        self.edit_avatar_btn.setText(self.T["edit_avatar"])
        self.clear_btn.setText(self.T["clear"])
        self.input_field.setPlaceholderText(self.T["send_placeholder"])
        self.lang_btn.setText("Русский" if self.lang == "ru" else "English")
        self.msg_count_label.setText(self.T["msg_count"].format(count=self.msg_counter))
        if hasattr(self, "bg_label"):
            self.bg_label.setText(self.T["background_label"])
            self.bg_speed_label.setText(self.T["background_speed"])
            self.bg_particles_cb.setText(self.T["background_particles"])
            self.bg_animate_cb.setText(self.T["background_animate"])
            self.bg_translucent_cb.setText(self.T["background_translucent"])
            # перестроить dropdown
            self._rebuild_bg_combo()

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

    def _rebuild_bg_combo(self):
        """Перестроить dropdown фонов при смене языка."""
        if not hasattr(self, "bg_combo"):
            return
        self.bg_combo.blockSignals(True)
        self.bg_combo.clear()
        self.bg_combo.addItem(self.T["background_none"], None)
        for bg_id, bg_data in BACKGROUNDS.items():
            # локализованное имя
            key = f"bg_{bg_id}"
            label = self.T.get(key, bg_data["name"])
            self.bg_combo.addItem(label, bg_id)
        # установить текущий
        idx = self.bg_combo.findData(self.bg_id)
        if idx >= 0:
            self.bg_combo.setCurrentIndex(idx)
        self.bg_combo.blockSignals(False)

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

        # === ФОН ===
        self.bg_label = QLabel(self.T["background_label"]); self.bg_label.setObjectName("muted")
        sl.addWidget(self.bg_label)

        self.bg_combo = QComboBox()
        self._rebuild_bg_combo()
        self.bg_combo.currentIndexChanged.connect(self._on_bg_combo_changed)
        sl.addWidget(self.bg_combo)

        # строка со скоростью
        speed_row = QHBoxLayout()
        speed_row.setSpacing(8)
        self.bg_speed_label = QLabel(self.T["background_speed"]); self.bg_speed_label.setObjectName("muted")
        speed_row.addWidget(self.bg_speed_label)
        self.bg_speed_slider = QSlider(Qt.Horizontal)
        self.bg_speed_slider.setMinimum(5)
        self.bg_speed_slider.setMaximum(60)
        self.bg_speed_slider.setValue(int(self.bg_speed))
        self.bg_speed_slider.valueChanged.connect(self._on_speed_change)
        speed_row.addWidget(self.bg_speed_slider, 1)
        self.bg_speed_value = QLabel(f"{int(self.bg_speed)}s")
        self.bg_speed_value.setObjectName("muted")
        self.bg_speed_value.setFixedWidth(36)
        speed_row.addWidget(self.bg_speed_value)
        sl.addLayout(speed_row)

        # чекбоксы
        self.bg_particles_cb = QCheckBox(self.T["background_particles"])
        self.bg_particles_cb.setChecked(self.bg_particles)
        self.bg_particles_cb.stateChanged.connect(self._toggle_particles)
        sl.addWidget(self.bg_particles_cb)

        self.bg_animate_cb = QCheckBox(self.T["background_animate"])
        self.bg_animate_cb.setChecked(self.bg_animate)
        self.bg_animate_cb.stateChanged.connect(self._toggle_animation)
        sl.addWidget(self.bg_animate_cb)

        self.bg_translucent_cb = QCheckBox(self.T["background_translucent"])
        self.bg_translucent_cb.setChecked(self.bg_translucent)
        self.bg_translucent_cb.stateChanged.connect(self._toggle_translucent)
        sl.addWidget(self.bg_translucent_cb)

        self.bg_status_label = QLabel("")
        self.bg_status_label.setObjectName("muted")
        sl.addWidget(self.bg_status_label)
        if self.bg_id and self.bg_id in BACKGROUNDS:
            self.bg_status_label.setText(BACKGROUNDS[self.bg_id]["name"])
        else:
            self.bg_status_label.setText(self.T["background_none"])

        sl.addWidget(self._sep())

        # === МОДЕЛЬ ===
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

        # === ПЕРСОНАЖ ===
        self.char_label = QLabel(self.T["character"]); self.char_label.setObjectName("muted")
        sl.addWidget(self.char_label)
        self.char_btn = QPushButton(self.T["create_character"])
        self.char_btn.clicked.connect(self.open_character)
        self.char_btn.setMinimumHeight(40)
        sl.addWidget(self.char_btn)

        self.char_combo = QComboBox()
        self.char_combo.addItem("— Без персонажа —", None)
        for cname in self.settings.get("characters", {}).keys():
            self.char_combo.addItem(f"👤 {cname}", cname)
        if self.current_character:
            idx = self.char_combo.findData(self.current_character.get("name"))
            if idx >= 0:
                self.char_combo.setCurrentIndex(idx)
        self.char_combo.currentIndexChanged.connect(self.on_character_selected)

        char_row = QHBoxLayout()
        char_row.setSpacing(6)
        char_row.addWidget(self.char_combo, 1)
        self.char_del_btn = QPushButton("🗑")
        self.char_del_btn.setObjectName("clear_btn")
        self.char_del_btn.setFixedWidth(40)
        self.char_del_btn.setMinimumHeight(38)
        self.char_del_btn.setCursor(Qt.PointingHandCursor)
        self.char_del_btn.clicked.connect(self.delete_character)
        self.char_del_btn.setToolTip("Удалить текущего персонажа")
        char_row.addWidget(self.char_del_btn)
        sl.addLayout(char_row)

        self.edit_char_btn = QPushButton(self.T["edit_character"])
        self.edit_char_btn.setObjectName("refresh_btn")
        self.edit_char_btn.setMinimumHeight(34)
        self.edit_char_btn.clicked.connect(self.edit_current_character)
        sl.addWidget(self.edit_char_btn)

        self.edit_avatar_btn = QPushButton(self.T["edit_avatar"])
        self.edit_avatar_btn.setObjectName("refresh_btn")
        self.edit_avatar_btn.setMinimumHeight(34)
        self.edit_avatar_btn.clicked.connect(self.edit_current_avatar)
        sl.addWidget(self.edit_avatar_btn)

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

        header = QWidget(); header.setObjectName("card"); header.setFixedHeight(70)
        hl = QHBoxLayout(header); hl.setContentsMargins(20, 10, 20, 10)
        hl.setSpacing(14)

        title = QLabel("✦ NeoBrain"); title.setObjectName("title")
        hl.addWidget(title)
        version = QLabel("v8.0"); version.setObjectName("muted")
        hl.addWidget(version)

        sep = QLabel("│"); sep.setObjectName("muted")
        hl.addWidget(sep)

        self.header_avatar = AvatarWidget(
            self.current_character.get("name", "") if self.current_character else "",
            size=48,
            palette_key=self.current_theme,
            style_key=self.current_style,
            is_user=False,
            character=self.current_character
        )
        hl.addWidget(self.header_avatar)

        info_col = QVBoxLayout()
        info_col.setContentsMargins(0, 0, 0, 0)
        info_col.setSpacing(2)

        self.header_char_name = QLabel(
            self.current_character.get("name", "Без персонажа") if self.current_character else "Без персонажа"
        )
        self.header_char_name.setStyleSheet("font-size: 15px; font-weight: 700; background: transparent;")
        info_col.addWidget(self.header_char_name)

        self.header_char_desc = QLabel(
            self.current_character.get("personality", "Выберите персонажа") if self.current_character
            else "Выберите персонажа в настройках"
        )
        self.header_char_desc.setObjectName("muted")
        self.header_char_desc.setStyleSheet("font-size: 11px; background: transparent;")
        info_col.addWidget(self.header_char_desc)

        hl.addLayout(info_col)
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

    def _on_bg_combo_changed(self, index):
        bg_id = self.bg_combo.itemData(index)
        self._apply_background(bg_id)

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
        if hasattr(self, "background") and self.background is not None:
            self.background.setGeometry(self.rect())
            self.background.lower()

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

    def _ai_name(self):
        if self.current_character:
            return self.current_character.get("name", "NeoBrain")
        return "NeoBrain"

    def _is_ai_sender(self, sender):
        if sender in ("NeoBrain", "✦ NeoBrain"):
            return True
        if self.current_character and sender == self.current_character.get("name"):
            return True
        return False

    def add_system_message(self, sender, text):
        self.add_message(sender, text, is_system=True)

    def add_message(self, sender, text, restore=False, is_system=False):
        if not restore:
            self._current_history().append({"sender": sender, "text": text})
            self.msg_counter += 1
            self.msg_count_label.setText(self.T["msg_count"].format(count=self.msg_counter))
            self.save_history()

        is_user = not self._is_ai_sender(sender)

        if is_system:
            show_sender = False
            display_name = ""
        else:
            show_sender = True
            display_name = "Вы" if is_user else self._ai_name()

        if is_user:
            avatar_name = "Вы"
            avatar_char = None
        elif self.current_character:
            avatar_name = self.current_character.get("name", "NeoBrain")
            avatar_char = self.current_character
        else:
            avatar_name = "NeoBrain"
            avatar_char = None

        bubble = MessageBubble(text, is_user=is_user, sender=display_name,
                                palette_key=self.current_theme,
                                style_key=self.current_style,
                                show_sender=show_sender,
                                avatar_name=avatar_name,
                                character=avatar_char)
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
        self._current_history().clear()
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
    # ПЕРСОНАЖ (создание / редактирование)
    # ============================================================

    def open_character(self, checked=False, character_to_edit=None):
        is_edit = character_to_edit is not None
        char_old_name = character_to_edit.get("name") if is_edit else None

        dialog = QDialog(self)
        if is_edit:
            dialog.setWindowTitle(self.T["character_edit_title"])
        else:
            dialog.setWindowTitle(self.T["character_title"])
        dialog.setFixedSize(560, 700)
        dialog.setStyleSheet(build_qss(self.current_theme, self.current_style))

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)

        title_text = self.T["character_edit_title"] if is_edit else self.T["character_title"]
        t = QLabel(title_text); t.setObjectName("title")
        layout.addWidget(t)

        existing_path = get_avatar_path(char_old_name) if is_edit and char_old_name else None
        existing_pixmap = None
        if existing_path:
            pm_tmp = QPixmap(existing_path)
            if not pm_tmp.isNull():
                existing_pixmap = pm_tmp

        dlg_state = {
            "source_pixmap": existing_pixmap,
            "source_path": existing_path,
            "zoom": float(character_to_edit.get("avatar_zoom", 1.0)) if is_edit else 1.0,
            "offset_x": float(character_to_edit.get("avatar_offset_x", 0.0)) if is_edit else 0.0,
            "offset_y": float(character_to_edit.get("avatar_offset_y", 0.0)) if is_edit else 0.0,
        }

        avatar_hint = QLabel(self.T["avatar_hint"]); avatar_hint.setObjectName("muted")
        layout.addWidget(avatar_hint)

        avatar_row = QHBoxLayout()
        avatar_row.setSpacing(16)

        avatar_preview = QLabel()
        avatar_preview.setFixedSize(110, 110)
        avatar_preview.setAlignment(Qt.AlignCenter)
        avatar_preview.setStyleSheet(
            "background: rgba(255,255,255,0.05);"
            "border: 2px dashed rgba(255,255,255,0.15);"
            "border-radius: 55px;"
        )

        def set_preview(name_for_letter=""):
            src = dlg_state["source_pixmap"]
            if src is not None and not src.isNull():
                rounded = make_round_pixmap(
                    src, 110,
                    dlg_state["zoom"],
                    dlg_state["offset_x"],
                    dlg_state["offset_y"]
                )
                avatar_preview.setPixmap(rounded)
            else:
                name_now = name_for_letter or name_entry.text().strip() or "?"
                pm = make_letter_avatar(name_now, 110, "#8b5cf6", "#00d4ff")
                avatar_preview.setPixmap(pm)

        def pick_avatar():
            path, _ = QFileDialog.getOpenFileName(
                dialog, "Выбрать аватар", "",
                "Изображения (*.png *.jpg *.jpeg *.webp)"
            )
            if not path:
                return
            pm = QPixmap(path)
            if pm.isNull():
                QMessageBox.warning(dialog, "Ошибка", "Не удалось загрузить файл.")
                return
            dlg_state["source_pixmap"] = pm
            dlg_state["source_path"] = path
            dlg_state["zoom"] = 1.0
            dlg_state["offset_x"] = 0.0
            dlg_state["offset_y"] = 0.0

            editor = AvatarEditorDialog(
                pm,
                palette_key=self.current_theme,
                style_key=self.current_style,
                initial_zoom=1.0,
                initial_offset_x=0.0,
                initial_offset_y=0.0,
                parent=dialog
            )
            if editor.exec_() == QDialog.Accepted:
                result = editor.get_result()
                if result:
                    dlg_state["zoom"], dlg_state["offset_x"], dlg_state["offset_y"] = result
            set_preview()

        def reset_avatar():
            dlg_state["source_pixmap"] = None
            dlg_state["source_path"] = None
            dlg_state["zoom"] = 1.0
            dlg_state["offset_x"] = 0.0
            dlg_state["offset_y"] = 0.0
            set_preview(name_entry.text().strip())

        def edit_position():
            src = dlg_state["source_pixmap"]
            if src is None or src.isNull():
                QMessageBox.information(dialog, "Аватар", self.T["avatar_load_first"])
                return
            editor = AvatarEditorDialog(
                src,
                palette_key=self.current_theme,
                style_key=self.current_style,
                initial_zoom=dlg_state["zoom"],
                initial_offset_x=dlg_state["offset_x"],
                initial_offset_y=dlg_state["offset_y"],
                parent=dialog
            )
            if editor.exec_() == QDialog.Accepted:
                result = editor.get_result()
                if result:
                    dlg_state["zoom"], dlg_state["offset_x"], dlg_state["offset_y"] = result
                    set_preview()

        avatar_col = QVBoxLayout()
        avatar_col.setSpacing(8)

        pick_btn = QPushButton(self.T["avatar_upload"])
        pick_btn.setMinimumHeight(32)
        pick_btn.clicked.connect(pick_avatar)
        avatar_col.addWidget(pick_btn)

        edit_btn = QPushButton("🎨 Настроить")
        edit_btn.setObjectName("refresh_btn")
        edit_btn.setMinimumHeight(32)
        edit_btn.clicked.connect(edit_position)
        avatar_col.addWidget(edit_btn)

        reset_btn = QPushButton(self.T["avatar_reset"])
        reset_btn.setObjectName("refresh_btn")
        reset_btn.setMinimumHeight(32)
        reset_btn.clicked.connect(reset_avatar)
        avatar_col.addWidget(reset_btn)
        avatar_col.addStretch()

        avatar_row.addWidget(avatar_preview)
        avatar_row.addLayout(avatar_col)
        avatar_row.addStretch()
        layout.addLayout(avatar_row)

        layout.addWidget(QLabel(self.T["character_name"]))
        name_entry = QLineEdit(); name_entry.setMinimumHeight(42)
        layout.addWidget(name_entry)

        if is_edit and char_old_name:
            name_entry.setText(char_old_name)

        def on_name_changed(text):
            if dlg_state["source_pixmap"] is None:
                set_preview(text.strip() or "?")

        name_entry.textChanged.connect(on_name_changed)
        set_preview((char_old_name or "?"))

        layout.addWidget(QLabel(self.T["character_gender"]))
        ggroup = QButtonGroup(dialog)
        ggroup.setExclusive(True)
        gl = QHBoxLayout(); gl.setSpacing(14)

        male = QPushButton(self.T["character_male"])
        male.setCheckable(True); male.setFixedHeight(46)
        ggroup.addButton(male, 0)
        gl.addWidget(male)

        female = QPushButton(self.T["character_female"])
        female.setCheckable(True); female.setFixedHeight(46)
        ggroup.addButton(female, 1)
        gl.addWidget(female)
        gl.addStretch()
        layout.addLayout(gl)

        if is_edit:
            if character_to_edit.get("gender") == "женский":
                female.setChecked(True)
            else:
                male.setChecked(True)
        else:
            male.setChecked(True)

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
        if is_edit:
            p_entry.setText(character_to_edit.get("personality", ""))

        layout.addWidget(QLabel(self.T["character_desc"]))
        d_entry = QTextEdit(); d_entry.setMinimumHeight(70)
        layout.addWidget(d_entry)
        if is_edit:
            d_entry.setPlainText(character_to_edit.get("description", ""))

        layout.addStretch()
        bl = QHBoxLayout()

        save_label = self.T["character_save"] if is_edit else self.T["character_create"]
        save = QPushButton(save_label)
        save.clicked.connect(lambda: self.save_character(
            name_entry, ggroup, p_entry, d_entry, dialog,
            source_path=dlg_state["source_path"],
            zoom=dlg_state["zoom"],
            offset_x=dlg_state["offset_x"],
            offset_y=dlg_state["offset_y"],
            is_edit=is_edit,
            old_name=char_old_name,
        ))
        bl.addWidget(save)
        cancel = QPushButton(self.T["character_cancel"])
        cancel.clicked.connect(dialog.reject)
        bl.addWidget(cancel)
        layout.addLayout(bl)
        dialog.exec_()

    def save_character(self, name_entry, gender_group, personality_entry, desc_entry, dialog,
                        source_path=None, zoom=1.0, offset_x=0.0, offset_y=0.0,
                        is_edit=False, old_name=None):
        name = name_entry.text().strip()
        if not name:
            QMessageBox.warning(self, self.T["character_error"], self.T["character_error_name"])
            return

        chars = self.settings.get("characters", {})
        if (not is_edit and name in chars) or (is_edit and name != old_name and name in chars):
            QMessageBox.warning(
                self, self.T["character_error"],
                self.T["character_error_exists"].format(name=name)
            )
            return

        gender = "мужской" if gender_group.checkedId() == 0 else "женский"
        pronoun = "он" if gender == "мужской" else "она"
        personality = personality_entry.text().strip()
        desc = desc_entry.toPlainText().strip()

        prompt = self._generate_prompt(name, gender, personality, desc)

        old_history = []
        if is_edit and old_name and old_name in chars:
            old_history = chars[old_name].get("history", [])

        new_char = {
            "name": name,
            "gender": gender,
            "personality": personality,
            "description": desc,
            "prompt": prompt,
            "pronoun": pronoun,
            "history": old_history if is_edit else [],
            "avatar_zoom": float(zoom),
            "avatar_offset_x": float(offset_x),
            "avatar_offset_y": float(offset_y),
        }

        if source_path and os.path.exists(source_path):
            saved = save_avatar(name, source_path)
            if saved:
                new_char["avatar_path"] = saved

        if is_edit and old_name and old_name != name:
            rename_avatar_folder(old_name, name)
            new_path = get_avatar_path(name)
            if new_path:
                new_char["avatar_path"] = new_path

        if is_edit and old_name and old_name != name:
            if old_name in chars:
                del chars[old_name]

        self.settings["characters"][name] = new_char
        self.current_character = new_char
        self.settings["current_character"] = new_char
        self.save_settings()

        self._update_header_character()
        self.char_info.setText(f"✓ {name} ({gender})")

        if is_edit:
            if old_name and old_name != name:
                msg = self.T["character_renamed"].format(old=old_name, new=name)
            else:
                msg = self.T["character_updated"].format(name=name)
        else:
            msg = self.T["character_created"].format(name=name, gender=gender)
        self.add_system_message("✦ NeoBrain", msg)

        self._rebuild_char_combo(select_name=name)

        self._reload_chat()
        dialog.accept()

    def _rebuild_char_combo(self, select_name=None):
        self.char_combo.blockSignals(True)
        self.char_combo.clear()
        self.char_combo.addItem("— Без персонажа —", None)
        for cname in self.settings.get("characters", {}).keys():
            self.char_combo.addItem(f"👤 {cname}", cname)
        if select_name:
            idx = self.char_combo.findData(select_name)
            if idx >= 0:
                self.char_combo.setCurrentIndex(idx)
        self.char_combo.blockSignals(False)

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

        ai_avatar_name = (self.current_character.get("name", "NeoBrain")
                          if self.current_character else "NeoBrain")
        ai_bubble = MessageBubble("", is_user=False, sender=self._ai_name(),
                                   palette_key=self.current_theme,
                                   style_key=self.current_style,
                                   avatar_name=ai_avatar_name,
                                   character=self.current_character)
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
        for msg in self._current_history()[-10:]:
            if self._is_ai_sender(msg["sender"]):
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
            self._current_history().append({"sender": self._ai_name(), "text": response_text})
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