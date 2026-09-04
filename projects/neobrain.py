import sys
import json
import os
import threading
import requests
import subprocess
import time
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# ======================================================
# ЯЗЫКИ
# ======================================================

LANGUAGES = {
    "ru": {
        "title": "✦ NeoBrain",
        "settings": "✦ Настройки",
        "hide": "◀ Скрыть",
        "show": "▶ Показать",
        "theme": "🎯 Тема",
        "model": "🧠 Модель",
        "refresh": "🔄 Обновить модели",
        "stream": "💬 Потоковый ответ",
        "stream_check": "Включить плавный вывод",
        "character": "👤 Персонаж",
        "create_character": "➕ Создать персонажа",
        "clear": "🗑 Очистить чат",
        "send_placeholder": "Напишите сообщение… (Enter для отправки)",
        "status_ready": "✦ Готов к работе",
        "status_checking": "⏳ Проверка Ollama...",
        "status_ollama_ok": "✅ Ollama запущен",
        "status_ollama_error": "⚠️ Ollama не доступен",
        "status_launch": "⏳ Запуск Ollama...",
        "status_ollama_fail": "⚠️ Не удалось запустить Ollama",
        "status_ollama_started": "✅ Ollama запущен",
        "status_typing": "💬 Печатает...",
        "status_error": "❌ Ошибка: {e}",
        "character_title": "✦ Создать персонажа",
        "character_name": "👤 Имя персонажа:",
        "character_gender": "⚧ Пол:",
        "character_male": "♂ Мужской",
        "character_female": "♀ Женский",
        "character_personality": "🧠 Характер (личность):",
        "character_desc": "📝 Описание (как отвечает, стиль речи, манера):",
        "character_create": "✅ Создать",
        "character_cancel": "Отмена",
        "character_error": "Ошибка",
        "character_error_name": "Введите имя персонажа!",
        "character_created": "✅ Создан персонаж: {name} ({gender})",
        "msg_count": "Сообщений: {count}",
        "clear_confirm": "Очистка",
        "clear_confirm_text": "Удалить всю историю чата?",
        "chat_cleared": "Чат очищен.",
        "model_changed": "Модель изменена на: {model}",
        "theme_changed": "Тема изменена на: {theme}",
        "welcome": "Привет! Я твой AI-помощник. Начни диалог или выбери тему.",
    },
    "en": {
        "title": "✦ NeoBrain",
        "settings": "✦ Settings",
        "hide": "◀ Hide",
        "show": "▶ Show",
        "theme": "🎯 Theme",
        "model": "🧠 Model",
        "refresh": "🔄 Refresh models",
        "stream": "💬 Stream mode",
        "stream_check": "Enable smooth output",
        "character": "👤 Character",
        "create_character": "➕ Create character",
        "clear": "🗑 Clear chat",
        "send_placeholder": "Type a message… (Enter to send)",
        "status_ready": "✦ Ready",
        "status_checking": "⏳ Checking Ollama...",
        "status_ollama_ok": "✅ Ollama running",
        "status_ollama_error": "⚠️ Ollama unavailable",
        "status_launch": "⏳ Starting Ollama...",
        "status_ollama_fail": "⚠️ Failed to start Ollama",
        "status_ollama_started": "✅ Ollama started",
        "status_typing": "💬 Typing...",
        "status_error": "❌ Error: {e}",
        "character_title": "✦ Create character",
        "character_name": "👤 Character name:",
        "character_gender": "⚧ Gender:",
        "character_male": "♂ Male",
        "character_female": "♀ Female",
        "character_personality": "🧠 Personality:",
        "character_desc": "📝 Description (style, manner):",
        "character_create": "✅ Create",
        "character_cancel": "Cancel",
        "character_error": "Error",
        "character_error_name": "Enter character name!",
        "character_created": "✅ Character created: {name} ({gender})",
        "msg_count": "Messages: {count}",
        "clear_confirm": "Clear",
        "clear_confirm_text": "Delete entire chat history?",
        "chat_cleared": "Chat cleared.",
        "model_changed": "Model changed to: {model}",
        "theme_changed": "Theme changed to: {theme}",
        "welcome": "Hi! I'm your AI assistant. Start a conversation or choose a theme.",
    }
}

# ======================================================
# ТЕМЫ (ТОЛЬКО ВИЗУАЛ)
# ======================================================

THEMES = {
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

THEME_STYLES = {
    "🌆 Неон": """
        QMainWindow { background: #0a0512; }
        QWidget#card { background: rgba(20, 5, 30, 0.95); border: 1px solid rgba(255,45,138,0.5); border-radius: 18px; }
        QWidget#sidebar { background: rgba(10, 5, 20, 0.9); border-right: 1px solid rgba(255,45,138,0.3); }
        QPushButton { background: #ff2d8a; color: white; border: none; border-radius: 10px; padding: 10px; font-weight: 600; }
        QPushButton:hover { background: #ff4a9a; }
        QPushButton#send_btn { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff2d8a, stop:1 #d11a6a); color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 18px; font-weight: 700; }
        QPushButton#send_btn:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff4a9a, stop:1 #ff2d8a); }
        QPushButton#send_btn:disabled { background: #2a1a2a; color: #666; }
        QPushButton#stop_btn { background: #ff4757; color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 20px; font-weight: 700; }
        QPushButton#stop_btn:hover { background: #ff6b7b; }
        QLineEdit#input_field { background: rgba(10,5,20,0.95); border: 2px solid rgba(255,45,138,0.3); color: #ffb0d0; padding: 14px 20px; border-radius: 14px; font-size: 15px; }
        QLineEdit#input_field:focus { border: 2px solid #ff2d8a; }
        QLabel { color: #ffb0d0; }
        QComboBox { background: rgba(10,5,20,0.9); border: 1px solid rgba(255,45,138,0.3); color: #ffb0d0; padding: 8px 14px; border-radius: 10px; min-height: 38px; }
        QScrollBar:vertical { background: rgba(0,0,0,0.3); width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background: rgba(255,45,138,0.4); border-radius: 3px; }
        QScrollBar::handle:vertical:hover { background: rgba(255,45,138,0.6); }
        QStatusBar { color: #ff6b9a; }
    """,
    "🖤 Тёмная": """
        QMainWindow { background: #0a0a18; }
        QWidget#card { background: rgba(15, 15, 35, 0.95); border: 1px solid rgba(79,172,254,0.1); border-radius: 18px; }
        QWidget#sidebar { background: rgba(10, 10, 30, 0.9); border-right: 1px solid rgba(79,172,254,0.08); }
        QPushButton { background: #4facfe; color: white; border: none; border-radius: 10px; padding: 10px; font-weight: 600; }
        QPushButton:hover { background: #60b8ff; }
        QPushButton#send_btn { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4facfe, stop:1 #3b82f6); color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 18px; font-weight: 700; }
        QPushButton#send_btn:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #60b8ff, stop:1 #4facfe); }
        QPushButton#send_btn:disabled { background: #2a2a4a; color: #666; }
        QPushButton#stop_btn { background: #ff4757; color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 20px; font-weight: 700; }
        QPushButton#stop_btn:hover { background: #ff6b7b; }
        QLineEdit#input_field { background: rgba(8,8,20,0.95); border: 2px solid rgba(42,42,90,0.3); color: #eeeef8; padding: 14px 20px; border-radius: 14px; font-size: 15px; }
        QLineEdit#input_field:focus { border: 2px solid #4facfe; }
        QLabel { color: #eeeef8; }
        QComboBox { background: rgba(13,13,32,0.9); border: 1px solid rgba(42,42,90,0.3); color: #eeeef8; padding: 8px 14px; border-radius: 10px; min-height: 38px; }
        QScrollBar:vertical { background: rgba(0,0,0,0.3); width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background: rgba(255,255,255,0.2); border-radius: 3px; }
        QScrollBar::handle:vertical:hover { background: rgba(255,255,255,0.3); }
        QStatusBar { color: #666; }
    """,
    "🌃 Ночная": """
        QMainWindow { background: #0a0a20; }
        QWidget#card { background: rgba(10, 10, 30, 0.95); border: 1px solid rgba(100,100,200,0.1); border-radius: 18px; }
        QWidget#sidebar { background: rgba(5, 5, 20, 0.9); border-right: 1px solid rgba(100,100,200,0.08); }
        QPushButton { background: #6c5ce7; color: white; border: none; border-radius: 10px; padding: 10px; font-weight: 600; }
        QPushButton:hover { background: #7d6df7; }
        QPushButton#send_btn { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6c5ce7, stop:1 #5649b5); color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 18px; font-weight: 700; }
        QPushButton#send_btn:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7d6df7, stop:1 #6c5ce7); }
        QPushButton#send_btn:disabled { background: #1a1a2a; color: #666; }
        QPushButton#stop_btn { background: #ff4757; color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 20px; font-weight: 700; }
        QPushButton#stop_btn:hover { background: #ff6b7b; }
        QLineEdit#input_field { background: rgba(8,8,25,0.95); border: 2px solid rgba(60,60,120,0.3); color: #d0d0f0; padding: 14px 20px; border-radius: 14px; font-size: 15px; }
        QLineEdit#input_field:focus { border: 2px solid #6c5ce7; }
        QLabel { color: #d0d0f0; }
        QComboBox { background: rgba(10,10,25,0.9); border: 1px solid rgba(60,60,120,0.3); color: #d0d0f0; padding: 8px 14px; border-radius: 10px; min-height: 38px; }
        QScrollBar:vertical { background: rgba(0,0,0,0.3); width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background: rgba(255,255,255,0.15); border-radius: 3px; }
        QScrollBar::handle:vertical:hover { background: rgba(255,255,255,0.25); }
        QStatusBar { color: #666; }
    """,
    "💻 Киберпанк": """
        QMainWindow { background: #0a0f1a; }
        QWidget#card { background: rgba(10, 15, 30, 0.95); border: 1px solid rgba(0, 200, 255, 0.3); border-radius: 18px; }
        QWidget#sidebar { background: rgba(5, 10, 20, 0.9); border-right: 1px solid rgba(0, 200, 255, 0.2); }
        QPushButton { background: #00c8ff; color: #0a0f1a; border: none; border-radius: 10px; padding: 10px; font-weight: 600; }
        QPushButton:hover { background: #33d6ff; }
        QPushButton#send_btn { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00c8ff, stop:1 #0099cc); color: #0a0f1a; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 18px; font-weight: 700; }
        QPushButton#send_btn:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #33d6ff, stop:1 #00c8ff); }
        QPushButton#send_btn:disabled { background: #1a2a3a; color: #556; }
        QPushButton#stop_btn { background: #ff4757; color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 20px; font-weight: 700; }
        QPushButton#stop_btn:hover { background: #ff6b7b; }
        QLineEdit#input_field { background: rgba(5,10,20,0.95); border: 2px solid rgba(0, 200, 255, 0.25); color: #88ddff; padding: 14px 20px; border-radius: 14px; font-size: 15px; }
        QLineEdit#input_field:focus { border: 2px solid #00c8ff; }
        QLabel { color: #88ddff; }
        QComboBox { background: rgba(5,10,20,0.9); border: 1px solid rgba(0, 200, 255, 0.25); color: #88ddff; padding: 8px 14px; border-radius: 10px; min-height: 38px; }
        QScrollBar:vertical { background: rgba(0,0,0,0.3); width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background: rgba(0, 200, 255, 0.3); border-radius: 3px; }
        QScrollBar::handle:vertical:hover { background: rgba(0, 200, 255, 0.5); }
        QStatusBar { color: #44aacc; }
    """,
    "🔮 Фиолетовая": """
        QMainWindow { background: #0a0518; }
        QWidget#card { background: rgba(20, 10, 40, 0.95); border: 1px solid rgba(160,120,255,0.2); border-radius: 18px; }
        QWidget#sidebar { background: rgba(10, 5, 30, 0.9); border-right: 1px solid rgba(160,120,255,0.15); }
        QPushButton { background: #8b5cf6; color: white; border: none; border-radius: 10px; padding: 10px; font-weight: 600; }
        QPushButton:hover { background: #a07cf6; }
        QPushButton#send_btn { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8b5cf6, stop:1 #6d4bd6); color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 18px; font-weight: 700; }
        QPushButton#send_btn:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a07cf6, stop:1 #8b5cf6); }
        QPushButton#send_btn:disabled { background: #1a0a2a; color: #666; }
        QPushButton#stop_btn { background: #ff4757; color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 20px; font-weight: 700; }
        QPushButton#stop_btn:hover { background: #ff6b7b; }
        QLineEdit#input_field { background: rgba(10,5,30,0.95); border: 2px solid rgba(160,120,255,0.2); color: #d0c0f0; padding: 14px 20px; border-radius: 14px; font-size: 15px; }
        QLineEdit#input_field:focus { border: 2px solid #8b5cf6; }
        QLabel { color: #d0c0f0; }
        QComboBox { background: rgba(10,5,30,0.9); border: 1px solid rgba(160,120,255,0.2); color: #d0c0f0; padding: 8px 14px; border-radius: 10px; min-height: 38px; }
        QScrollBar:vertical { background: rgba(0,0,0,0.3); width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background: rgba(160,120,255,0.25); border-radius: 3px; }
        QScrollBar::handle:vertical:hover { background: rgba(160,120,255,0.4); }
        QStatusBar { color: #666; }
    """,
    "☀️ Светлая": """
        QMainWindow { background: #f0f4f8; }
        QWidget#card { background: rgba(255,255,255,0.92); border: 1px solid rgba(200,210,220,0.4); border-radius: 18px; }
        QWidget#sidebar { background: rgba(255,255,255,0.96); border-right: 1px solid rgba(200,210,220,0.5); }
        QPushButton { background: #3498db; color: white; border: none; border-radius: 10px; padding: 10px; font-weight: 600; }
        QPushButton:hover { background: #2980b9; }
        QPushButton#send_btn { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9); color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 18px; font-weight: 700; }
        QPushButton#send_btn:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4ab0eb, stop:1 #3498db); }
        QPushButton#send_btn:disabled { background: #ccc; color: #888; }
        QPushButton#stop_btn { background: #ff4757; color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 20px; font-weight: 700; }
        QPushButton#stop_btn:hover { background: #ff6b7b; }
        QLineEdit#input_field { background: #ffffff; border: 1px solid #dbe2e8; color: #2c3e50; padding: 14px 20px; border-radius: 14px; font-size: 15px; }
        QLineEdit#input_field:focus { border: 1px solid #3498db; }
        QLabel { color: #2c3e50; }
        QComboBox { background: #ffffff; border: 1px solid #dbe2e8; color: #2c3e50; padding: 8px 14px; border-radius: 10px; min-height: 38px; }
        QScrollBar:vertical { background: rgba(200,200,200,0.3); width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background: rgba(0,0,0,0.2); border-radius: 3px; }
        QScrollBar::handle:vertical:hover { background: rgba(0,0,0,0.3); }
        QStatusBar { color: #888; }
    """,
    "🌸 Розовая": """
        QMainWindow { background: #fdf0f5; }
        QWidget#card { background: rgba(255,245,250,0.95); border: 1px solid rgba(255,180,200,0.4); border-radius: 18px; }
        QWidget#sidebar { background: rgba(255,240,248,0.96); border-right: 1px solid rgba(255,180,200,0.3); }
        QPushButton { background: #e87a9a; color: white; border: none; border-radius: 10px; padding: 10px; font-weight: 600; }
        QPushButton:hover { background: #f08aaa; }
        QPushButton#send_btn { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e87a9a, stop:1 #d06a8a); color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 18px; font-weight: 700; }
        QPushButton#send_btn:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f08aaa, stop:1 #e87a9a); }
        QPushButton#send_btn:disabled { background: #d0b0b8; color: #888; }
        QPushButton#stop_btn { background: #ff4757; color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 20px; font-weight: 700; }
        QPushButton#stop_btn:hover { background: #ff6b7b; }
        QLineEdit#input_field { background: #ffffff; border: 1px solid #f0d0dd; color: #4a2a3a; padding: 14px 20px; border-radius: 14px; font-size: 15px; }
        QLineEdit#input_field:focus { border: 1px solid #e87a9a; }
        QLabel { color: #4a2a3a; }
        QComboBox { background: #ffffff; border: 1px solid #f0d0dd; color: #4a2a3a; padding: 8px 14px; border-radius: 10px; min-height: 38px; }
        QScrollBar:vertical { background: rgba(200,200,200,0.3); width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background: rgba(0,0,0,0.15); border-radius: 3px; }
        QScrollBar::handle:vertical:hover { background: rgba(0,0,0,0.25); }
        QStatusBar { color: #888; }
    """,
    "🌊 Морская": """
        QMainWindow { background: #e8f4f8; }
        QWidget#card { background: rgba(240,250,255,0.95); border: 1px solid rgba(100,200,220,0.4); border-radius: 18px; }
        QWidget#sidebar { background: rgba(235,248,255,0.96); border-right: 1px solid rgba(100,200,220,0.3); }
        QPushButton { background: #3aa8c8; color: white; border: none; border-radius: 10px; padding: 10px; font-weight: 600; }
        QPushButton:hover { background: #4ab8d8; }
        QPushButton#send_btn { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3aa8c8, stop:1 #2a98b8); color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 18px; font-weight: 700; }
        QPushButton#send_btn:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4ab8d8, stop:1 #3aa8c8); }
        QPushButton#send_btn:disabled { background: #a0c8d0; color: #888; }
        QPushButton#stop_btn { background: #ff4757; color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 20px; font-weight: 700; }
        QPushButton#stop_btn:hover { background: #ff6b7b; }
        QLineEdit#input_field { background: #ffffff; border: 1px solid #c0e0e8; color: #1a3a4a; padding: 14px 20px; border-radius: 14px; font-size: 15px; }
        QLineEdit#input_field:focus { border: 1px solid #3aa8c8; }
        QLabel { color: #1a3a4a; }
        QComboBox { background: #ffffff; border: 1px solid #c0e0e8; color: #1a3a4a; padding: 8px 14px; border-radius: 10px; min-height: 38px; }
        QScrollBar:vertical { background: rgba(200,200,200,0.3); width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background: rgba(0,0,0,0.15); border-radius: 3px; }
        QScrollBar::handle:vertical:hover { background: rgba(0,0,0,0.25); }
        QStatusBar { color: #888; }
    """,
    "🌿 Мятная": """
        QMainWindow { background: #e8f5f0; }
        QWidget#card { background: rgba(240,255,248,0.95); border: 1px solid rgba(100,210,180,0.4); border-radius: 18px; }
        QWidget#sidebar { background: rgba(235,255,245,0.96); border-right: 1px solid rgba(100,210,180,0.3); }
        QPushButton { background: #3aaa8a; color: white; border: none; border-radius: 10px; padding: 10px; font-weight: 600; }
        QPushButton:hover { background: #4aba9a; }
        QPushButton#send_btn { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3aaa8a, stop:1 #2a9a7a); color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 18px; font-weight: 700; }
        QPushButton#send_btn:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4aba9a, stop:1 #3aaa8a); }
        QPushButton#send_btn:disabled { background: #a0d0c0; color: #888; }
        QPushButton#stop_btn { background: #ff4757; color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 20px; font-weight: 700; }
        QPushButton#stop_btn:hover { background: #ff6b7b; }
        QLineEdit#input_field { background: #ffffff; border: 1px solid #c0e8dd; color: #1a3a32; padding: 14px 20px; border-radius: 14px; font-size: 15px; }
        QLineEdit#input_field:focus { border: 1px solid #3aaa8a; }
        QLabel { color: #1a3a32; }
        QComboBox { background: #ffffff; border: 1px solid #c0e8dd; color: #1a3a32; padding: 8px 14px; border-radius: 10px; min-height: 38px; }
        QScrollBar:vertical { background: rgba(200,200,200,0.3); width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background: rgba(0,0,0,0.15); border-radius: 3px; }
        QScrollBar::handle:vertical:hover { background: rgba(0,0,0,0.25); }
        QStatusBar { color: #888; }
    """,
    "☕ Кремовая": """
        QMainWindow { background: #f5eee8; }
        QWidget#card { background: rgba(255,248,240,0.95); border: 1px solid rgba(210,190,170,0.4); border-radius: 18px; }
        QWidget#sidebar { background: rgba(255,245,235,0.96); border-right: 1px solid rgba(210,190,170,0.3); }
        QPushButton { background: #b89070; color: white; border: none; border-radius: 10px; padding: 10px; font-weight: 600; }
        QPushButton:hover { background: #c8a080; }
        QPushButton#send_btn { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #b89070, stop:1 #a88060); color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 18px; font-weight: 700; }
        QPushButton#send_btn:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #c8a080, stop:1 #b89070); }
        QPushButton#send_btn:disabled { background: #d0c0b0; color: #888; }
        QPushButton#stop_btn { background: #ff4757; color: white; border: none; border-radius: 30px; min-width: 52px; min-height: 52px; font-size: 20px; font-weight: 700; }
        QPushButton#stop_btn:hover { background: #ff6b7b; }
        QLineEdit#input_field { background: #ffffff; border: 1px solid #e0d0c0; color: #3a2a1a; padding: 14px 20px; border-radius: 14px; font-size: 15px; }
        QLineEdit#input_field:focus { border: 1px solid #b89070; }
        QLabel { color: #3a2a1a; }
        QComboBox { background: #ffffff; border: 1px solid #e0d0c0; color: #3a2a1a; padding: 8px 14px; border-radius: 10px; min-height: 38px; }
        QScrollBar:vertical { background: rgba(200,200,200,0.3); width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background: rgba(0,0,0,0.15); border-radius: 3px; }
        QScrollBar::handle:vertical:hover { background: rgba(0,0,0,0.25); }
        QStatusBar { color: #888; }
    """
}

# ======================================================
# ВИДЖЕТ СООБЩЕНИЯ (ПУЗЫРЁК)
# ======================================================

class MessageBubble(QWidget):
    def __init__(self, text, is_user=False, theme="🌆 Неон", parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.theme = theme

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 4, 6, 4)
        main_layout.setSpacing(0)

        bubble_container = QWidget()
        bubble_container.setStyleSheet("background: transparent; border: none;")
        bubble_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        bubble_layout = QVBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)

        self.bubble = QWidget()
        self.bubble.setMaximumWidth(700)
        self.bubble.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        is_light_theme = any([
            "☀️" in theme,
            "🌸" in theme,
            "🌊" in theme,
            "🌿" in theme,
            "☕" in theme
        ])

        if is_user:
            self.bubble.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db, stop:1 #2980b9);
                    border-radius: 18px;
                    border-top-right-radius: 4px;
                }
            """)
            text_color = "#ffffff"
        else:
            if is_light_theme:
                self.bubble.setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(220, 220, 230, 0.8),
                            stop:1 rgba(200, 200, 210, 0.6));
                        border-radius: 18px;
                        border-top-left-radius: 4px;
                        border: 1px solid rgba(180, 180, 190, 0.3);
                    }
                """)
                text_color = "#1a1a1a"
            else:
                self.bubble.setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(255, 255, 255, 0.12),
                            stop:1 rgba(255, 255, 255, 0.06));
                        border-radius: 18px;
                        border-top-left-radius: 4px;
                        border: 1px solid rgba(255, 255, 255, 0.05);
                    }
                """)
                text_color = "#eeeef8"

        bubble_layout_inner = QVBoxLayout(self.bubble)
        bubble_layout_inner.setContentsMargins(16, 12, 16, 12)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMinimumWidth(0)
        self.label.setStyleSheet(f"""
            color: {text_color};
            font-size: 15px;
            font-family: 'Segoe UI', sans-serif;
            background: transparent;
        """)
        bubble_layout_inner.addWidget(self.label)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40 if is_user else 30))
        shadow.setOffset(0, 4)
        self.bubble.setGraphicsEffect(shadow)

        bubble_layout.addWidget(self.bubble)

        if is_user:
            main_layout.addStretch()
            main_layout.addWidget(bubble_container)
        else:
            main_layout.addWidget(bubble_container)
            main_layout.addStretch()

    def set_text(self, text):
        self.label.setText(text)

# ======================================================
# ОСНОВНОЙ КЛАСС
# ======================================================

class NeoBrainChat(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "ru"
        self.T = LANGUAGES[self.lang]

        self.setWindowTitle(self.T["title"])
        self.resize(1200, 800)
        self.setMinimumSize(960, 600)

        self.settings = self.load_settings()
        self.model = self.settings.get("model", "llama3.2:3b")
        self.ollama_url = self.settings.get("ollama_url", "http://localhost:11434")
        self.temperature = self.settings.get("temperature", 0.7)
        self.current_theme = self.settings.get("theme", "🌆 Неон")
        self.message_history = self.settings.get("history", [])
        self.msg_counter = len(self.message_history)

        self.sidebar_visible = True
        self.sidebar_width = 260
        self.models = ["llama3.2:3b"]
        self.characters = self.settings.get("characters", {})
        self.current_character = self.settings.get("current_character", None)
        self.fade_anim = None
        self.is_animating = False
        self.sidebar_anim = None
        self.sidebar_max_anim = None
        self.is_generating = False
        self.stop_generation = False

        self.setup_ui()
        self.apply_theme(self.current_theme, instant=True)

        self.status_text.setText(self.T["status_checking"])
        if self.ensure_ollama_running():
            self.status_text.setText(self.T["status_ollama_ok"])
            threading.Thread(target=self.load_models, daemon=True).start()
        else:
            self.status_text.setText(self.T["status_ollama_error"])

        self.add_system_message("✦ NeoBrain", self.T["welcome"])

        if self.message_history:
            for msg in self.message_history:
                self.add_message(msg.get("sender", "NeoBrain"), msg.get("text", ""), restore=True)

    # ============================================================
    # ЯЗЫК
    # ============================================================

    def toggle_language(self):
        self.lang = "en" if self.lang == "ru" else "ru"
        self.T = LANGUAGES[self.lang]
        self.update_ui_texts()

    def update_ui_texts(self):
        self.setWindowTitle(self.T["title"])
        self.panel_title.setText(self.T["settings"])
        self.toggle_btn.setText(self.T["hide"])
        self.theme_label.setText(self.T["theme"])
        self.model_label.setText(self.T["model"])
        self.refresh_btn.setText(self.T["refresh"])
        self.stream_label.setText(self.T["stream"])
        self.stream_checkbox.setText(self.T["stream_check"])
        self.char_label.setText(self.T["character"])
        self.char_btn.setText(self.T["create_character"])
        self.clear_btn.setText(self.T["clear"])
        self.input_field.setPlaceholderText(self.T["send_placeholder"])
        self.status_text.setText(self.T["status_ready"])

    # ============================================================
    # АВТОЗАПУСК OLLAMA
    # ============================================================

    def ensure_ollama_running(self):
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if resp.status_code == 200:
                return True
        except:
            pass

        self.status_text.setText(self.T["status_launch"])
        QApplication.processEvents()

        try:
            if os.name == 'nt':
                subprocess.Popen(
                    ["ollama", "serve"],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )

            for _ in range(20):
                time.sleep(0.5)
                try:
                    resp = requests.get(f"{self.ollama_url}/api/tags", timeout=1)
                    if resp.status_code == 200:
                        self.status_text.setText(self.T["status_ollama_started"])
                        return True
                except:
                    pass

            self.status_text.setText(self.T["status_ollama_fail"])
            return False

        except Exception as e:
            self.status_text.setText(self.T["status_error"].format(e=e))
            return False

    # ============================================================
    # ЗАГРУЗКА/СОХРАНЕНИЕ
    # ============================================================

    def load_settings(self):
        path = os.path.join(os.path.dirname(__file__), "neobrain_settings.json")
        default = {
            "ollama_url": "http://localhost:11434",
            "model": "llama3.2:3b",
            "temperature": 0.7,
            "theme": "🌆 Неон",
            "current_character": None,
            "characters": {},
            "history": [],
            "auto_save": True,
            "stream_mode": True,
            "max_tokens": 512
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
            path = os.path.join(os.path.dirname(__file__), "neobrain_settings.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def save_history(self):
        MAX_HISTORY = 100
        if self.settings.get("auto_save", True):
            self.settings["history"] = self.message_history[-MAX_HISTORY:]
            self.save_settings()

    # ============================================================
    # МОДЕЛИ
    # ============================================================

    def load_models(self):
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            resp.raise_for_status()
            self.models = [m["name"] for m in resp.json().get("models", [])]
            if not self.models:
                self.models = ["llama3.2:3b"]
        except Exception:
            self.models = ["llama3.2:3b"]

        QMetaObject.invokeMethod(self, "update_model_combo", Qt.QueuedConnection)

    @Slot()
    def update_model_combo(self):
        self.model_combo.clear()
        self.model_combo.addItems(self.models)
        if self.model in self.models:
            self.model_combo.setCurrentText(self.model)
        else:
            self.model_combo.setCurrentIndex(0)
            self.model = self.models[0]
            self.settings["model"] = self.model
            self.save_settings()

    # ============================================================
    # ТЕМЫ
    # ============================================================

    def create_theme_menu(self):
        menu = QMenu(self)

        dark_menu = QMenu("🌙 Тёмные", menu)
        dark_themes = [t for t in THEMES.keys() if "🌆" in t or "🖤" in t or "🌃" in t or "💻" in t or "🔮" in t]
        for theme in sorted(dark_themes):
            action = dark_menu.addAction(theme)
            action.triggered.connect(lambda checked, t=theme: self.apply_theme(t))
        menu.addMenu(dark_menu)

        light_menu = QMenu("☀️ Светлые", menu)
        light_themes = [t for t in THEMES.keys() if "☀️" in t or "🌸" in t or "🌊" in t or "🌿" in t or "☕" in t]
        for theme in sorted(light_themes):
            action = light_menu.addAction(theme)
            action.triggered.connect(lambda checked, t=theme: self.apply_theme(t))
        menu.addMenu(light_menu)

        return menu

    def show_theme_menu(self):
        menu = self.create_theme_menu()
        menu.exec_(self.theme_btn.mapToGlobal(self.theme_btn.rect().bottomLeft()))

    def apply_theme(self, theme_name, instant=False):
        self.current_theme = theme_name
        self.settings["theme"] = theme_name
        self.save_settings()
        self.status_label.setText(f"🎯 {theme_name}")
        self.theme_btn.setText(f"🎯 {theme_name}")

        style = THEME_STYLES.get(theme_name, THEME_STYLES["🌆 Неон"])

        if instant:
            self.setStyleSheet(style)
        else:
            self.smooth_switch_theme(style)
        self.add_system_message("✦ NeoBrain", self.T["theme_changed"].format(theme=theme_name))

    def smooth_switch_theme(self, new_style):
        if self.is_animating:
            return

        self.is_animating = True

        if not hasattr(self, 'opacity_effect'):
            self.opacity_effect = QGraphicsOpacityEffect()
            self.centralWidget().setGraphicsEffect(self.opacity_effect)

        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(150)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.2)
        self.fade_anim.finished.connect(
            lambda: self.apply_and_fade_in(new_style)
        )
        self.fade_anim.start()

    def apply_and_fade_in(self, new_style):
        self.setStyleSheet(new_style)

        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(200)
        self.fade_anim.setStartValue(0.2)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.finished.connect(
            lambda: setattr(self, 'is_animating', False)
        )
        self.fade_anim.start()

    # ============================================================
    # UI
    # ============================================================

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== БОКОВАЯ ПАНЕЛЬ =====
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(self.sidebar_width)
        self.sidebar.setMinimumWidth(0)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(16)

        self.panel_title = QLabel(self.T["settings"])
        self.panel_title.setStyleSheet("font-size: 20px; font-weight: 700; color: #4facfe;")
        sidebar_layout.addWidget(self.panel_title)

        self.toggle_btn = QPushButton(self.T["hide"])
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.toggle_btn.setMinimumHeight(42)
        sidebar_layout.addWidget(self.toggle_btn)

        sidebar_layout.addSpacing(10)

        self.theme_label = QLabel(self.T["theme"])
        self.theme_label.setStyleSheet("color: #888; font-size: 13px; font-weight: 600;")
        sidebar_layout.addWidget(self.theme_label)

        self.theme_btn = QPushButton(f"🎯 {self.current_theme}")
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background: rgba(13,13,32,0.9);
                border: 1px solid rgba(42,42,90,0.3);
                border-radius: 10px;
                padding: 8px 14px;
                color: #eeeef8;
                text-align: left;
                min-height: 38px;
                font-weight: 500;
            }
            QPushButton:hover {
                border: 1px solid #4facfe;
            }
            QPushButton::menu-indicator {
                image: none;
            }
        """)
        self.theme_btn.clicked.connect(self.show_theme_menu)
        sidebar_layout.addWidget(self.theme_btn)

        sidebar_layout.addSpacing(10)

        self.model_label = QLabel(self.T["model"])
        self.model_label.setStyleSheet("color: #888; font-size: 13px; font-weight: 600;")
        sidebar_layout.addWidget(self.model_label)

        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.change_model)
        sidebar_layout.addWidget(self.model_combo)

        self.refresh_btn = QPushButton(self.T["refresh"])
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: rgba(79, 172, 254, 0.15);
                color: #4facfe;
                border: 1px solid rgba(79, 172, 254, 0.3);
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover { background: rgba(79, 172, 254, 0.3); }
        """)
        self.refresh_btn.clicked.connect(lambda: threading.Thread(target=self.load_models, daemon=True).start())
        sidebar_layout.addWidget(self.refresh_btn)

        sidebar_layout.addSpacing(10)

        self.stream_label = QLabel(self.T["stream"])
        self.stream_label.setStyleSheet("color: #888; font-size: 13px; font-weight: 600;")
        sidebar_layout.addWidget(self.stream_label)

        self.stream_checkbox = QCheckBox(self.T["stream_check"])
        self.stream_checkbox.setStyleSheet("color: #eeeef8; font-size: 13px;")
        self.stream_checkbox.setChecked(self.settings.get("stream_mode", True))
        self.stream_checkbox.stateChanged.connect(self.toggle_stream_mode)
        sidebar_layout.addWidget(self.stream_checkbox)

        sidebar_layout.addSpacing(10)

        self.char_label = QLabel(self.T["character"])
        self.char_label.setStyleSheet("color: #888; font-size: 13px; font-weight: 600;")
        sidebar_layout.addWidget(self.char_label)

        self.char_btn = QPushButton(self.T["create_character"])
        self.char_btn.clicked.connect(self.open_character)
        self.char_btn.setMinimumHeight(40)
        sidebar_layout.addWidget(self.char_btn)

        self.char_info = QLabel("")
        self.char_info.setStyleSheet("color: #34d399; font-size: 13px;")
        sidebar_layout.addWidget(self.char_info)

        if self.current_character:
            self.char_info.setText(f"✓ {self.current_character.get('name', '')}")

        sidebar_layout.addStretch()

        self.clear_btn = QPushButton(self.T["clear"])
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #ff4757;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
            }
            QPushButton:hover { background: #ff6b7b; }
        """)
        self.clear_btn.clicked.connect(self.clear_history)
        sidebar_layout.addWidget(self.clear_btn)

        main_layout.addWidget(self.sidebar)

        # ===== ОСНОВНАЯ ОБЛАСТЬ =====
        main_content = QWidget()
        main_layout.addWidget(main_content)

        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setContentsMargins(12, 12, 12, 12)
        main_content_layout.setSpacing(12)

        header = QWidget()
        header.setObjectName("card")
        header.setFixedHeight(64)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 10, 24, 10)

        title = QLabel("✦ NeoBrain")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #4facfe;")
        header_layout.addWidget(title)

        version = QLabel("v7.3")
        version.setStyleSheet("color: #666; font-size: 11px;")
        header_layout.addWidget(version)

        header_layout.addStretch()

        self.status_label = QLabel(f"🎯 {self.current_theme}")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        header_layout.addWidget(self.status_label)

        self.indicator = QLabel("●")
        self.indicator.setStyleSheet("color: #34d399; font-size: 14px;")
        header_layout.addWidget(self.indicator)

        main_content_layout.addWidget(header)

        chat_widget = QWidget()
        chat_widget.setObjectName("card")
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(16, 16, 16, 16)
        chat_layout.setSpacing(0)

        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_scroll_area.setStyleSheet("border: none; background: transparent;")

        self.chat_container = QWidget()
        self.chat_container_layout = QVBoxLayout(self.chat_container)
        self.chat_container_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_container_layout.setSpacing(8)
        self.chat_container_layout.setAlignment(Qt.AlignTop)

        self.chat_scroll_area.setWidget(self.chat_container)
        chat_layout.addWidget(self.chat_scroll_area)
        main_content_layout.addWidget(chat_widget)

        bottom = QWidget()
        bottom.setFixedHeight(64)
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(20, 0, 20, 0)
        bottom_layout.setSpacing(12)

        self.input_field = QLineEdit()
        self.input_field.setObjectName("input_field")
        self.input_field.setPlaceholderText(self.T["send_placeholder"])
        self.input_field.returnPressed.connect(self.send_message)
        bottom_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("➤")
        self.send_btn.setObjectName("send_btn")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:1 #3b82f6);
                color: white;
                border: none;
                border-radius: 30px;
                min-width: 52px;
                min-height: 52px;
                font-size: 18px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #60b8ff, stop:1 #4facfe);
            }
            QPushButton:disabled {
                background: #2a2a4a;
                color: #666;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        bottom_layout.addWidget(self.send_btn)

        # Кнопка остановки (скрыта по умолчанию)
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setVisible(False)
        self.stop_btn.clicked.connect(self.stop_generation_handler)
        bottom_layout.addWidget(self.stop_btn)

        main_content_layout.addWidget(bottom)

        self.sidebar_trigger_btn = QPushButton("▶")
        self.sidebar_trigger_btn.setFixedSize(28, 56)
        self.sidebar_trigger_btn.setStyleSheet("""
            QPushButton {
                background: rgba(79, 172, 254, 0.15);
                border: 1px solid rgba(79,172,254,0.3);
                border-left: none;
                border-radius: 0 14px 14px 0;
                color: #4facfe;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(79, 172, 254, 0.3);
                border-color: #4facfe;
            }
        """)
        self.sidebar_trigger_btn.setVisible(False)
        self.sidebar_trigger_btn.setParent(self)
        self.sidebar_trigger_btn.clicked.connect(self.toggle_sidebar)

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        self.status_text = QLabel(self.T["status_ready"])
        self.status_text.setStyleSheet("color: #666; font-size: 11px;")
        status_bar.addWidget(self.status_text)

        status_bar.addPermanentWidget(QLabel("|"))

        self.msg_count_label = QLabel(self.T["msg_count"].format(count=self.msg_counter))
        self.msg_count_label.setStyleSheet("color: #666; font-size: 11px;")
        status_bar.addPermanentWidget(self.msg_count_label)

        self.typing_label = QLabel("")
        self.typing_label.setStyleSheet("color: #22d3ee; font-size: 11px;")
        status_bar.addPermanentWidget(self.typing_label)

        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim.setDuration(350)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

    # ============================================================
    # ПАНЕЛЬ + ЯМКА
    # ============================================================

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        target_width = self.sidebar_width if self.sidebar_visible else 0

        if self.sidebar_anim:
            self.sidebar_anim.stop()
            self.sidebar_anim.deleteLater()
        if self.sidebar_max_anim:
            self.sidebar_max_anim.stop()
            self.sidebar_max_anim.deleteLater()

        self.sidebar_anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_anim.setDuration(350)
        self.sidebar_anim.setStartValue(self.sidebar.minimumWidth())
        self.sidebar_anim.setEndValue(target_width)
        self.sidebar_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.sidebar_anim.start()

        self.sidebar_max_anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_max_anim.setDuration(350)
        self.sidebar_max_anim.setStartValue(self.sidebar.maximumWidth())
        self.sidebar_max_anim.setEndValue(target_width)
        self.sidebar_max_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.sidebar_max_anim.start()

        if self.sidebar_visible:
            self.sidebar_trigger_btn.setVisible(False)
            self.toggle_btn.setText(self.T["hide"])
        else:
            self.toggle_btn.setText(self.T["show"])
            self.sidebar_trigger_btn.setVisible(True)
            self.sidebar_trigger_btn.setText("▶")
            y_pos = self.height() // 2 - 28
            self.sidebar_trigger_btn.move(0, y_pos)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.sidebar_visible:
            y_pos = self.height() // 2 - 28
            self.sidebar_trigger_btn.move(0, y_pos)

    # ============================================================
    # ПОТОКОВЫЙ РЕЖИМ И ОСТАНОВКА
    # ============================================================

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

        is_user = (sender != "NeoBrain")
        bubble = MessageBubble(text, is_user=is_user, theme=self.current_theme)
        self.chat_container_layout.addWidget(bubble)
        QTimer.singleShot(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        sb = self.chat_scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    def clear_history(self):
        reply = QMessageBox.question(
            self, self.T["clear_confirm"], self.T["clear_confirm_text"],
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
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
        self.model = text
        self.settings["model"] = text
        self.save_settings()
        self.add_system_message("✦ NeoBrain", self.T["model_changed"].format(model=text))

    # ============================================================
    # ПЕРСОНАЖИ
    # ============================================================

    def open_character(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.T["character_title"])
        dialog.setFixedSize(520, 520)
        dialog.setStyleSheet(THEME_STYLES.get(self.current_theme, THEME_STYLES["🌆 Неон"]))

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)

        title = QLabel(self.T["character_title"])
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #4facfe;")
        layout.addWidget(title)

        name_label = QLabel(self.T["character_name"])
        name_label.setStyleSheet("color: #888; font-size: 13px; font-weight: 600;")
        layout.addWidget(name_label)

        name_entry = QLineEdit()
        name_entry.setPlaceholderText("Например: Алиса, Профессор Смит, Макс...")
        name_entry.setMinimumHeight(42)
        name_entry.setStyleSheet("""
            QLineEdit {
                background: rgba(13,13,32,0.8);
                border: 1px solid rgba(42,42,90,0.3);
                border-radius: 10px;
                padding: 10px 16px;
                color: #eeeef8;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4facfe;
            }
        """)
        layout.addWidget(name_entry)

        gender_label = QLabel(self.T["character_gender"])
        gender_label.setStyleSheet("color: #888; font-size: 13px; font-weight: 600;")
        layout.addWidget(gender_label)

        gender_group = QButtonGroup(dialog)
        gender_layout = QHBoxLayout()
        gender_layout.setSpacing(16)

        male_btn = QPushButton(self.T["character_male"])
        male_btn.setCheckable(True)
        male_btn.setChecked(True)
        male_btn.setFixedHeight(48)
        male_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(79, 172, 254, 0.15),
                    stop:1 rgba(79, 172, 254, 0.05));
                border: 2px solid rgba(79, 172, 254, 0.3);
                border-radius: 12px;
                color: #4facfe;
                font-size: 15px;
                font-weight: 600;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(79, 172, 254, 0.35),
                    stop:1 rgba(79, 172, 254, 0.15));
                border: 2px solid #4facfe;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe,
                    stop:1 #3b82f6);
                color: white;
                border: 2px solid #4facfe;
            }
        """)
        gender_group.addButton(male_btn)
        gender_layout.addWidget(male_btn)

        female_btn = QPushButton(self.T["character_female"])
        female_btn.setCheckable(True)
        female_btn.setFixedHeight(48)
        female_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 107, 157, 0.15),
                    stop:1 rgba(255, 107, 157, 0.05));
                border: 2px solid rgba(255, 107, 157, 0.3);
                border-radius: 12px;
                color: #ff6b9d;
                font-size: 15px;
                font-weight: 600;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 107, 157, 0.35),
                    stop:1 rgba(255, 107, 157, 0.15));
                border: 2px solid #ff6b9d;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b9d,
                    stop:1 #e0558a);
                color: white;
                border: 2px solid #ff6b9d;
            }
        """)
        gender_group.addButton(female_btn)
        gender_layout.addWidget(female_btn)

        gender_group.setExclusive(True)
        gender_layout.addStretch()
        layout.addLayout(gender_layout)

        personality_label = QLabel(self.T["character_personality"])
        personality_label.setStyleSheet("color: #888; font-size: 13px; font-weight: 600;")
        layout.addWidget(personality_label)

        personality_entry = QLineEdit()
        personality_entry.setPlaceholderText("Например: добрый, отзывчивый, любит шутить, циничный...")
        personality_entry.setMinimumHeight(42)
        personality_entry.setStyleSheet("""
            QLineEdit {
                background: rgba(13,13,32,0.8);
                border: 1px solid rgba(42,42,90,0.3);
                border-radius: 10px;
                padding: 10px 16px;
                color: #eeeef8;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4facfe;
            }
        """)
        layout.addWidget(personality_entry)

        desc_label = QLabel(self.T["character_desc"])
        desc_label.setStyleSheet("color: #888; font-size: 13px; font-weight: 600;")
        layout.addWidget(desc_label)

        desc_entry = QTextEdit()
        desc_entry.setPlaceholderText("Например: говорит коротко и по делу, использует юмор, любит философствовать...")
        desc_entry.setMinimumHeight(80)
        desc_entry.setStyleSheet("""
            QTextEdit {
                background: rgba(13,13,32,0.8);
                border: 1px solid rgba(42,42,90,0.3);
                border-radius: 10px;
                padding: 10px 14px;
                color: #eeeef8;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 1px solid #4facfe;
            }
        """)
        layout.addWidget(desc_entry)

        layout.addStretch()

        btn_layout = QHBoxLayout()

        save_btn = QPushButton(self.T["character_create"])
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:1 #3b82f6);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 30px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #60b8ff, stop:1 #4facfe);
            }
        """)
        save_btn.clicked.connect(
            lambda: self.save_character(name_entry, gender_group, personality_entry, desc_entry, dialog)
        )
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton(self.T["character_cancel"])
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #2a2a5a;
                border-radius: 10px;
                padding: 10px 24px;
                color: #8a8ab0;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.05);
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        dialog.exec_()

    def save_character(self, name_entry, gender_group, personality_entry, desc_entry, dialog):
        name = name_entry.text().strip()
        if not name:
            QMessageBox.warning(self, self.T["character_error"], self.T["character_error_name"])
            return

        gender = "мужской" if gender_group.buttons()[0].isChecked() else "женский"
        pronoun = "он" if gender == "мужской" else "она"

        personality = personality_entry.text().strip()
        desc = desc_entry.toPlainText().strip()

        prompt = f"Ты персонаж по имени {name}."
        if personality:
            prompt += f" Ты {pronoun} {personality}."
        if desc:
            prompt += f" {desc}"
        prompt += f" Ты {pronoun}. Отвечай в этом образе."

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
    # ОТПРАВКА СООБЩЕНИЯ
    # ============================================================

    def send_message(self):
        text = self.input_field.text().strip()
        if not text or self.is_generating:
            return

        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.is_generating = True
        self.stop_generation = False

        # Меняем кнопку отправки на кнопку остановки
        self.send_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        self.typing_label.setText(self.T["status_typing"])

        self.add_message("Вы", text)

        ai_bubble = MessageBubble("", is_user=False, theme=self.current_theme)
        self.chat_container_layout.addWidget(ai_bubble)
        self.scroll_to_bottom()

        thread = threading.Thread(target=self.stream_response, args=(text, ai_bubble), daemon=True)
        thread.start()

    def stream_response(self, user_text, ai_bubble):
        system_prompt = THEMES.get(self.current_theme, "")
        max_tokens = self.settings.get("max_tokens", 512)

        if self.current_character:
            system_prompt += "\n" + self.current_character.get("prompt", "")

        full_prompt = ""

        if system_prompt:
            full_prompt += f"System: {system_prompt}\n"

        recent_history = self.message_history[-10:]
        for msg in recent_history:
            if msg["sender"] == "NeoBrain":
                full_prompt += f"Assistant: {msg['text']}\n"
            else:
                full_prompt += f"User: {msg['text']}\n"

        full_prompt += f"User: {user_text}\nAssistant:"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": self.temperature,
                "num_predict": max_tokens
            }
        }

        stream_mode = self.settings.get("stream_mode", True)

        try:
            with requests.post(f"{self.ollama_url}/api/generate", json=payload, stream=True, timeout=60) as r:
                if r.status_code == 200:
                    response_text = ""

                    if stream_mode:
                        for line in r.iter_lines():
                            if self.stop_generation:
                                break
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    chunk = data.get('response', '')
                                    if chunk:
                                        response_text += chunk
                                        ai_bubble.set_text(response_text)
                                        self.scroll_to_bottom()
                                        QApplication.processEvents()
                                        time.sleep(0.01)
                                except json.JSONDecodeError:
                                    continue
                    else:
                        for line in r.iter_lines():
                            if self.stop_generation:
                                break
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    chunk = data.get('response', '')
                                    if chunk:
                                        response_text += chunk
                                except json.JSONDecodeError:
                                    continue
                        if not self.stop_generation:
                            ai_bubble.set_text(response_text)
                            self.scroll_to_bottom()
                else:
                    ai_bubble.set_text(f"⚠️ Ошибка API: {r.status_code}")

            # Если остановили генерацию — убираем сообщение
            if self.stop_generation:
                if ai_bubble:
                    ai_bubble.set_text("⏹ Генерация остановлена")

        except requests.exceptions.ConnectionError:
            ai_bubble.set_text("❌ Не удалось подключиться к Ollama.\nЗапусти: `ollama serve`")
        except requests.exceptions.Timeout:
            ai_bubble.set_text("⏰ Таймаут. Модель думает слишком долго.")
        except Exception as e:
            ai_bubble.set_text(f"❌ Ошибка: {str(e)}")
        finally:
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

# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = NeoBrainChat()
    window.show()
    sys.exit(app.exec_())