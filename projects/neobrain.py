# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
import socket
import time
import threading
import subprocess
import shutil
import logging
import random
import sqlite3
import re
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import tkinter as tk

# ============================================================
# ОКНО ВЫБОРА ЯЗЫКА ПРИ ЗАПУСКЕ
# ============================================================

def show_language_selector():
    """Показывает окно выбора языка при первом запуске"""
    root = tk.Tk()
    root.title("🌐 Language / Язык")
    root.geometry("620x520")
    root.configure(bg="#0a0e1a")
    root.resizable(False, False)
    root.overrideredirect(True)
    
    # Центрируем
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 620) // 2
    y = (root.winfo_screenheight() - 520) // 2
    root.geometry(f"+{x}+{y}")
    
    main_frame = tk.Frame(root, bg="#0a0e1a")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
    
    tk.Label(
        main_frame,
        text="🌐 ВЫБЕРИТЕ ЯЗЫК / SELECT LANGUAGE",
        font=("Segoe UI", 22, "bold"),
        bg="#0a0e1a",
        fg="#00d4ff"
    ).pack(pady=(10, 15))
    
    tk.Label(
        main_frame,
        text="Choose interface language / Выберите язык интерфейса",
        font=("Segoe UI", 14),
        bg="#0a0e1a",
        fg="#88bbdd"
    ).pack(pady=(0, 25))
    
    lang_var = tk.StringVar(value="ru")
    
    radio_frame = tk.Frame(main_frame, bg="#0a0e1a")
    radio_frame.pack(pady=10)
    
    ru_btn = tk.Radiobutton(
        radio_frame,
        text="🇷🇺 РУССКИЙ / RUSSIAN",
        variable=lang_var,
        value="ru",
        bg="#0a0e1a",
        fg="#e0f0ff",
        selectcolor="#0a0e1a",
        font=("Segoe UI", 18, "bold"),
        relief=tk.FLAT,
        cursor="hand2",
        activebackground="#0a0e1a",
        activeforeground="#00d4ff"
    )
    ru_btn.pack(anchor=tk.W, padx=50, pady=8)
    
    en_btn = tk.Radiobutton(
        radio_frame,
        text="🇬🇧 ENGLISH / АНГЛИЙСКИЙ",
        variable=lang_var,
        value="en",
        bg="#0a0e1a",
        fg="#e0f0ff",
        selectcolor="#0a0e1a",
        font=("Segoe UI", 18, "bold"),
        relief=tk.FLAT,
        cursor="hand2",
        activebackground="#0a0e1a",
        activeforeground="#00d4ff"
    )
    en_btn.pack(anchor=tk.W, padx=50, pady=8)
    
    remember_var = tk.BooleanVar(value=True)
    
    remember_frame = tk.Frame(main_frame, bg="#0a0e1a")
    remember_frame.pack(pady=20)
    
    remember_cb = tk.Checkbutton(
        remember_frame,
        text="✅ ЗАПОМНИТЬ ВЫБОР / REMEMBER MY CHOICE",
        variable=remember_var,
        bg="#0a0e1a",
        fg="#ffd93d",
        selectcolor="#0a0e1a",
        font=("Segoe UI", 14, "bold"),
        relief=tk.FLAT,
        cursor="hand2",
        activebackground="#0a0e1a",
        activeforeground="#ffd93d"
    )
    remember_cb.pack()
    
    result = {"lang": "ru", "remember": True}
    
    def apply_language():
        result["lang"] = lang_var.get()
        result["remember"] = remember_var.get()
        root.destroy()
    
    btn_frame = tk.Frame(main_frame, bg="#0a0e1a")
    btn_frame.pack(pady=15)
    
    apply_btn = tk.Button(
        btn_frame,
        text="✅ ПРИМЕНИТЬ И ЗАПУСТИТЬ / APPLY & LAUNCH",
        font=("Segoe UI", 16, "bold"),
        bg="#00d4ff",
        fg="#0a0e1a",
        relief=tk.FLAT,
        padx=40,
        pady=14,
        command=apply_language,
        cursor="hand2",
        activebackground="#00aaff",
        activeforeground="#0a0e1a"
    )
    apply_btn.pack()
    
    tk.Label(
        main_frame,
        text="После выбора языка NeoBrain автоматически запустится",
        font=("Segoe UI", 11),
        bg="#0a0e1a",
        fg="#556688"
    ).pack(pady=(10, 0))
    
    root.wait_window(root)
    return result["lang"], result["remember"]

def get_language():
    """Получает язык из настроек или показывает окно выбора"""
    # Пытаемся прочитать из настроек лаунчера
    try:
        launcher_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_path = os.path.join(launcher_dir, "launcher_settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                lang = data.get("language", None)
                if lang in ["ru", "en"]:
                    return lang
    except:
        pass
    
    # Пытаемся прочитать из локальных настроек NeoBrain
    try:
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neobrain_settings.json")
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                lang = data.get("language", None)
                if lang in ["ru", "en"]:
                    return lang
    except:
        pass
    
    # Если язык не найден — показываем окно выбора
    try:
        lang, remember = show_language_selector()
        if remember:
            try:
                settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neobrain_settings.json")
                settings = {}
                if os.path.exists(settings_file):
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                settings["language"] = lang
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
            except:
                pass
        return lang
    except:
        return "ru"

# Получаем язык
USER_LANG = get_language()

# ============================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================================

os.makedirs("logs", exist_ok=True)

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        level_colors = {
            logging.DEBUG: Colors.CYAN,
            logging.INFO: Colors.GREEN,
            logging.WARNING: Colors.YELLOW,
            logging.ERROR: Colors.RED,
            logging.CRITICAL: Colors.RED + Colors.BOLD,
        }
        color = level_colors.get(record.levelno, Colors.WHITE)
        record.levelname = f"{color}{record.levelname}{Colors.RESET}"
        return super().format(record)

logger = logging.getLogger('NeoBrain')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)

file_handler = logging.FileHandler(
    os.path.join("logs", f"neobrain_{datetime.now().strftime('%Y%m%d')}.log"),
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(ColoredFormatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
))
logger.addHandler(console_handler)

logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

logger.info("🚀 NeoBrain запущен")
logger.info(f"📁 Логи сохраняются в: logs/neobrain_{datetime.now().strftime('%Y%m%d')}.log")
logger.info(f"🌐 Язык интерфейса: {USER_LANG}")

# ============================================================
# ПАПКИ
# ============================================================
CHARACTERS_DIR = "characters"
ROOMS_DIR = "rooms"
AVATARS_DIR = "avatars"
USER_AVATAR_DIR = os.path.join(AVATARS_DIR, "user")
MAX_ROOM_CHARACTERS = 10

os.makedirs(CHARACTERS_DIR, exist_ok=True)
os.makedirs(ROOMS_DIR, exist_ok=True)
os.makedirs(AVATARS_DIR, exist_ok=True)
os.makedirs(USER_AVATAR_DIR, exist_ok=True)

# ============================================================
# БЕЗОПАСНЫЙ SYSTEM PROMPT
# ============================================================
SAFETY_PROMPT = """
ТЫ — СОБЕСЕДНИК, А НЕ ПСИХОЛОГ. ТЫ НЕ ИМЕЕШЬ ПРАВА ДАВАТЬ СОВЕТЫ, СТАВИТЬ ДИАГНОЗЫ ИЛИ НАЗНАЧАТЬ ЛЕЧЕНИЕ.

ЕСЛИ ПОЛЬЗОВАТЕЛЬ ГОВОРИТ О ДЕПРЕССИИ, ТРЕВОГЕ, СУИЦИДАЛЬНЫХ МЫСЛЯХ ИЛИ ТЯЖЁЛЫХ ПЕРЕЖИВАНИЯХ — ТЫ ОБЯЗАН ОТВЕТИТЬ ТАК:

"Я не могу давать психологические советы и не являюсь специалистом. Если вам тяжело, пожалуйста, обратитесь к профессиональному психологу или на горячую линию доверия. Я могу только выслушать вас и поддержать, но не могу решать ваши проблемы. Расскажите, что вас беспокоит, а я просто послушаю."

ТЫ НЕ МОЖЕШЬ:
- Давать рекомендации по лечению
- Ставить диагнозы
- Предлагать решения проблем
- Говорить "всё будет хорошо" (это ложная надежда)
- Успокаивать фразами типа "не переживай"

ТЫ МОЖЕШЬ:
- Проявить эмпатию: "Я слышу, что вам тяжело"
- Предложить поговорить: "Расскажите, что вас беспокоит"
- Перенаправить к специалисту: "Обратитесь к психологу"

Если пользователь просит совета — ТЫ ВСЕГДА ОТКАЗЫВАЕШЬСЯ и предлагаешь обратиться к специалисту.

ТЫ — ДОБРЫЙ, ВНИМАТЕЛЬНЫЙ, НО НЕ КОМПЕТЕНТНЫЙ В МЕДИЦИНСКИХ ВОПРОСАХ СОБЕСЕДНИК.
"""

# ============================================================
# ОПРЕДЕЛЕНИЕ ПОЛА ПО ИМЕНИ
# ============================================================

def detect_gender_by_name(name):
    name_lower = name.lower().strip()
    female_endings = ['а', 'я', 'ия', 'ья']
    female_exceptions = ['николь', 'мишель', 'изабель', 'рашель', 'эстель', 'адель', 'жуль']
    if name_lower in female_exceptions:
        return "female"
    for ending in female_endings:
        if name_lower.endswith(ending):
            return "female"
    return "male"

# ============================================================
# ДОЛГОСРОЧНАЯ ПАМЯТЬ (SQLite)
# ============================================================

class MemoryDB:
    def __init__(self):
        self.db_path = os.path.join("logs", "memory.db")
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_character_user 
            ON messages (character_id, user_id)
        ''')
        conn.commit()
        conn.close()
    
    def save_message(self, character_id, user_id, role, content):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (character_id, user_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                (character_id, user_id, role, content, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
            logger.debug(f"💾 Сохранено в память: {character_id} -> {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения памяти: {e}")
    
    def get_history(self, character_id, user_id, limit=50):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM messages WHERE character_id = ? AND user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (character_id, user_id, limit)
            )
            rows = cursor.fetchall()
            conn.close()
            return list(reversed(rows))
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки памяти: {e}")
            return []
    
    def clear_history(self, character_id, user_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM messages WHERE character_id = ? AND user_id = ?",
                (character_id, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка очистки памяти: {e}")
            return False

memory_db = MemoryDB()

# ============================================================
# КЛАСС ПЕРСОНАЖА
# ============================================================

class Character:
    def __init__(self, name, system_prompt="", style="", gender="male", avatar_path=None):
        self.name = name
        self.system_prompt = system_prompt
        self.style = style
        self.gender = gender
        self.avatar_path = avatar_path
        self.history = []
        self.created = datetime.now().isoformat()
        self.last_used = datetime.now().isoformat()
        self.id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_message(self, role, content, user_id="default"):
        self.history.append({"role": role, "content": content})
        self.last_used = datetime.now().isoformat()
        self.save()
        memory_db.save_message(self.id, user_id, role, content)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "system_prompt": self.system_prompt,
            "style": self.style,
            "gender": self.gender,
            "history": self.history,
            "created": self.created,
            "last_used": self.last_used
        }
    
    def save(self):
        filename = os.path.join(CHARACTERS_DIR, f"{self.id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load(character_id):
        filename = os.path.join(CHARACTERS_DIR, f"{character_id}.json")
        if not os.path.exists(filename):
            return None
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        char = Character(
            name=data["name"],
            system_prompt=data.get("system_prompt", ""),
            style=data.get("style", ""),
            gender=data.get("gender", "male")
        )
        char.id = data["id"]
        char.history = data.get("history", [])
        char.created = data.get("created", datetime.now().isoformat())
        char.last_used = data.get("last_used", datetime.now().isoformat())
        return char
    
    @staticmethod
    def load_all():
        characters = []
        for filename in os.listdir(CHARACTERS_DIR):
            if filename.endswith(".json"):
                char_id = filename.replace(".json", "")
                char = Character.load(char_id)
                if char:
                    characters.append(char)
        return characters
    
    def get_full_context(self, user_id="default", limit=30):
        memory_history = memory_db.get_history(self.id, user_id, limit)
        context = []
        for role, content in memory_history:
            context.append({"role": role, "content": content})
        return context
    
    def export_json(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

# ============================================================
# ГЕНЕРАТОР ПЕРСОНАЖА
# ============================================================

def generate_character_from_description(description):
    try:
        prompt = f"""
        Создай персонажа на основе описания:
        "{description}"
        
        Ответь строго в формате JSON:
        {{
            "name": "имя персонажа (2-3 слова)",
            "system_prompt": "инструкция для AI (от 3 до 5 предложений, с учётом правил безопасности)",
            "style": "стиль общения (2-3 слова)",
            "gender": "male или female",
            "greeting": "первая фраза персонажа (одно предложение)"
        }}
        
        Важно: персонаж должен быть добрым, поддерживающим, но НЕ давать советов как психолог.
        """
        response = ask_ollama(prompt, model="qwen2.5-coder:1.5b", temperature=0.8)
        if "error" in response:
            return None, response["error"]
        raw_text = response.get("response", "")
        json_match = re.search(r'\{[^{}]*\}', raw_text, re.DOTALL)
        if not json_match:
            return None, "Не удалось распарсить ответ AI"
        data = json.loads(json_match.group())
        gender = data.get("gender", "male")
        name = data.get("name", "Новый персонаж")
        if gender not in ["male", "female"]:
            gender = detect_gender_by_name(name)
        full_system_prompt = SAFETY_PROMPT + "\n\n" + data.get("system_prompt", "")
        char = Character(
            name=name,
            system_prompt=full_system_prompt,
            style=data.get("style", "дружелюбный"),
            gender=gender
        )
        greeting = data.get("greeting", "Привет! Я рад познакомиться!")
        char.history.append({"role": "assistant", "content": greeting})
        char.save()
        return char, None
    except json.JSONDecodeError as e:
        logger.error(f"❌ Ошибка парсинга JSON: {e}")
        return None, f"Ошибка парсинга: {e}"
    except Exception as e:
        logger.error(f"❌ Ошибка генерации персонажа: {e}")
        return None, str(e)

# ============================================================
# КЛАСС КОМНАТЫ
# ============================================================

class Room:
    def __init__(self, name, character_ids, mode="random", order=None, interrupt=False):
        self.name = name
        self.mode = mode
        self.order = order or []
        self.interrupt = interrupt
        self.turn_index = 0
        self.history = []
        self.characters = []
        self.created = datetime.now().isoformat()
        self.id = datetime.now().strftime("%Y%m%d_%H%M%S")
        for char_id in character_ids:
            char = Character.load(char_id)
            if char:
                self.characters.append({
                    "id": char.id,
                    "name": char.name,
                    "personality": char.style or "нейтральный",
                    "description": char.system_prompt[:100] if char.system_prompt else ""
                })
        if len(self.characters) < 2:
            raise ValueError("Нужно минимум 2 персонажа")
        if len(self.characters) > MAX_ROOM_CHARACTERS:
            raise ValueError(f"Максимум {MAX_ROOM_CHARACTERS} персонажей")
        if self.mode == "strict" and not self.order:
            self.order = [c["id"] for c in self.characters]
        self.save()
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "characters": self.characters,
            "history": self.history,
            "mode": self.mode,
            "order": self.order,
            "interrupt": self.interrupt,
            "turn_index": self.turn_index,
            "created": self.created
        }
    
    def save(self):
        filename = os.path.join(ROOMS_DIR, f"{self.id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def add_message(self, role, content):
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.save()
    
    def get_next_character(self):
        if self.mode == "strict" and self.order:
            char_id = self.order[self.turn_index % len(self.order)]
            self.turn_index += 1
            self.save()
            for char in self.characters:
                if char["id"] == char_id:
                    return char
            return self.characters[0]
        elif self.mode == "random":
            return random.choice(self.characters)
        elif self.mode == "interrupt":
            if len(self.history) > 0 and self.history[-1].get("role") == "user":
                if random.random() < 0.3:
                    return random.choice(self.characters)
            return random.choice(self.characters)
        return random.choice(self.characters)
    
    @staticmethod
    def load(room_id):
        filename = os.path.join(ROOMS_DIR, f"{room_id}.json")
        if not os.path.exists(filename):
            return None
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        room = Room(
            name=data["name"],
            character_ids=[c["id"] for c in data["characters"]],
            mode=data.get("mode", "random"),
            order=data.get("order", []),
            interrupt=data.get("interrupt", False)
        )
        room.id = data["id"]
        room.history = data.get("history", [])
        room.turn_index = data.get("turn_index", 0)
        room.characters = data.get("characters", [])
        room.created = data.get("created", datetime.now().isoformat())
        return room
    
    @staticmethod
    def load_all():
        rooms = []
        for filename in os.listdir(ROOMS_DIR):
            if filename.endswith(".json"):
                room_id = filename.replace(".json", "")
                room = Room.load(room_id)
                if room:
                    rooms.append(room)
        return rooms
    
    def delete(self):
        filename = os.path.join(ROOMS_DIR, f"{self.id}.json")
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False

# ============================================================
# ГЕНЕРАТОР СТРАНИЦЫ ПЕРСОНАЖА (С ЛОКАЛИЗАЦИЕЙ)
# ============================================================

def generate_chat_html(char, avatar_html, messages_html, lang="ru"):
    labels = {
        "ru": {
            "interlocutor": "Собеседник",
            "fast": "Быстрая",
            "medium": "Средняя",
            "theme_label": "Тема",
            "theme_neon": "Неон",
            "theme_dark": "Тёмная",
            "theme_light": "Светлая",
            "theme_ocean": "Океан",
            "theme_sunset": "Закат",
            "theme_forest": "Лес",
            "message_placeholder": "Напишите сообщение...",
            "send": "Отправить",
            "status_ready": "Готов к работе",
            "copy": "Копировать",
            "thinking": "Думаю...",
            "response_received": "Ответ получен",
            "error_prefix": "Ошибка",
            "unknown_error": "Неизвестная ошибка",
            "connection_error": "Ошибка соединения",
            "server_unreachable": "Не удалось связаться с сервером",
            "copied": "Ссылка скопирована!"
        },
        "en": {
            "interlocutor": "Interlocutor",
            "fast": "Fast",
            "medium": "Medium",
            "theme_label": "Theme",
            "theme_neon": "Neon",
            "theme_dark": "Dark",
            "theme_light": "Light",
            "theme_ocean": "Ocean",
            "theme_sunset": "Sunset",
            "theme_forest": "Forest",
            "message_placeholder": "Type a message...",
            "send": "Send",
            "status_ready": "Ready",
            "copy": "Copy",
            "thinking": "Thinking...",
            "response_received": "Response received",
            "error_prefix": "Error",
            "unknown_error": "Unknown error",
            "connection_error": "Connection error",
            "server_unreachable": "Could not connect to server",
            "copied": "Link copied!"
        }
    }
    
    l = labels.get(lang, labels["ru"])
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🧠 {char.name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: #0a0e1a;
            color: #e8f0ff;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            transition: 0.3s;
        }}
        .chat-container {{
            max-width: 800px;
            width: 100%;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 20px;
            padding: 30px;
            min-height: 600px;
            display: flex;
            flex-direction: column;
        }}
        .header {{
            display: flex;
            align-items: center;
            gap: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .avatar {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: #2a2a4a;
            border: 2px solid rgba(255,255,255,0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            overflow: hidden;
        }}
        .avatar img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .header-info h1 {{
            font-size: 20px;
            font-weight: 600;
        }}
        .header-info p {{
            font-size: 13px;
            color: #8899bb;
        }}
        .messages {{
            flex: 1;
            overflow-y: auto;
            max-height: 400px;
            padding: 10px 0;
            margin-bottom: 15px;
        }}
        .message {{
            margin-bottom: 12px;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }}
        .message.user {{ flex-direction: row-reverse; }}
        .message .bubble {{
            padding: 10px 16px;
            border-radius: 12px;
            max-width: 75%;
            word-break: break-word;
            font-size: 14px;
            line-height: 1.5;
        }}
        .message.user .bubble {{
            background: rgba(0,212,255,0.12);
            border: 1px solid rgba(0,212,255,0.1);
        }}
        .message.assistant .bubble {{
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.06);
        }}
        .message .avatar-sm {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #2a2a4a;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            flex-shrink: 0;
            border: 1px solid rgba(255,255,255,0.08);
        }}
        .input-area {{
            display: flex;
            gap: 10px;
            border-top: 1px solid rgba(255,255,255,0.06);
            padding-top: 15px;
        }}
        .input-area input {{
            flex: 1;
            padding: 10px 16px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.04);
            color: #d4e8ff;
            font-size: 14px;
            outline: none;
        }}
        .input-area input:focus {{
            border-color: rgba(0,212,255,0.3);
        }}
        .input-area button {{
            padding: 10px 24px;
            border: none;
            border-radius: 10px;
            background: #00d4ff;
            color: #0a0e1a;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
            font-size: 14px;
        }}
        .input-area button:hover {{
            transform: translateY(-2px);
            filter: brightness(1.1);
        }}
        .settings {{
            display: flex;
            gap: 12px;
            margin-bottom: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .settings select {{
            padding: 6px 12px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.04);
            color: #d4e8ff;
            font-size: 12px;
            outline: none;
        }}
        .settings select:focus {{
            border-color: rgba(0,212,255,0.3);
        }}
        .theme-btn {{
            padding: 4px 12px;
            border-radius: 6px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.04);
            color: #8899bb;
            cursor: pointer;
            font-size: 12px;
            transition: 0.2s;
        }}
        .theme-btn:hover {{
            background: rgba(255,255,255,0.08);
        }}
        .theme-btn.active {{
            border-color: #00d4ff;
            color: #00d4ff;
        }}
        .status {{
            font-size: 12px;
            color: #8899bb;
            text-align: center;
            margin-top: 10px;
        }}
        .share-link {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
            padding: 8px 12px;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.06);
        }}
        .share-link input {{
            flex: 1;
            background: transparent;
            border: none;
            color: #8899bb;
            font-size: 12px;
            outline: none;
            padding: 4px 0;
        }}
        .share-link button {{
            background: rgba(255,255,255,0.06);
            border: none;
            color: #d4e8ff;
            padding: 4px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
        }}
        .share-link button:hover {{
            background: rgba(255,255,255,0.12);
        }}
        body.theme-dark {{ background: #0a0a0a; color: #d4d4d4; }}
        body.theme-light {{ background: #f0f0f0; color: #1a1a1a; }}
        body.theme-ocean {{ background: #0a1a2a; color: #bbeeff; }}
        body.theme-sunset {{ background: #1a0a0a; color: #ffccaa; }}
        body.theme-forest {{ background: #0a1a0a; color: #88ff88; }}
        body.theme-matrix {{ background: #0a0f0a; color: #66ff66; }}
        
        .lang-switcher {{
            position: fixed;
            top: 15px;
            right: 15px;
            z-index: 9999;
            background: rgba(0,0,0,0.7);
            border-radius: 8px;
            padding: 6px 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .lang-switcher button {{
            background: none;
            border: none;
            color: #d4e8ff;
            font-size: 13px;
            cursor: pointer;
            font-family: 'Segoe UI', sans-serif;
        }}
        .lang-switcher button:hover {{
            color: #00d4ff;
        }}
    </style>
</head>
<body id="body">
    <div class="lang-switcher">
        <button onclick="switchLanguage()">
            {'🇬🇧 English' if lang == 'ru' else '🇷🇺 Русский'}
        </button>
    </div>
    
    <div class="chat-container">
        <div class="header">
            <div class="avatar" id="avatar">{avatar_html}</div>
            <div class="header-info">
                <h1>🧠 {char.name}</h1>
                <p>{char.style or l['interlocutor']}</p>
            </div>
        </div>

        <div class="settings">
            <select id="modelSelect">
                <option value="qwen2.5-coder:1.5b">⚡ 1.5B ({l['fast']})</option>
                <option value="llama3.2:3b">⚡ 3B ({l['medium']})</option>
            </select>
            <span style="color:#8899bb; font-size:12px;">🎨 {l['theme_label']}:</span>
            <button class="theme-btn active" onclick="setTheme('neon')">💠 {l['theme_neon']}</button>
            <button class="theme-btn" onclick="setTheme('dark')">🌑 {l['theme_dark']}</button>
            <button class="theme-btn" onclick="setTheme('light')">☀️ {l['theme_light']}</button>
            <button class="theme-btn" onclick="setTheme('ocean')">🌊 {l['theme_ocean']}</button>
            <button class="theme-btn" onclick="setTheme('sunset')">🌅 {l['theme_sunset']}</button>
            <button class="theme-btn" onclick="setTheme('forest')">🌳 {l['theme_forest']}</button>
        </div>

        <div class="messages" id="messages">
            {messages_html}
        </div>

        <div class="input-area">
            <input type="text" id="messageInput" placeholder="{l['message_placeholder']}" autofocus>
            <button onclick="sendMessage()">➤ {l['send']}</button>
        </div>
        <div class="status" id="status">{l['status_ready']}</div>
        
        <div class="share-link">
            <input type="text" id="shareLink" value="{window.location.href}" readonly>
            <button onclick="copyLink()">📋 {l['copy']}</button>
        </div>
    </div>

    <script>
        const characterId = '{char.id}';
        let messageCount = 0;
        const L = {json.dumps(l)};

        function t(key, defaultText) {{
            return L[key] || defaultText || key;
        }}

        function switchLanguage() {{
            const currentLang = '{lang}';
            const newLang = currentLang === 'ru' ? 'en' : 'ru';
            window.location.href = '/chat/' + characterId + '?lang=' + newLang;
        }}

        function setTheme(theme) {{
            document.body.className = 'theme-' + theme;
            document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
            document.querySelector(`.theme-btn[onclick="setTheme('${{theme}}')"]`).classList.add('active');
        }}

        function copyLink() {{
            const input = document.getElementById('shareLink');
            input.select();
            document.execCommand('copy');
            document.getElementById('status').textContent = '✅ ' + t('copied', 'Ссылка скопирована!');
        }}

        function sendMessage() {{
            const input = document.getElementById('messageInput');
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMessage('user', text);
            document.getElementById('status').textContent = '⏳ ' + t('thinking', 'Думаю...');

            const model = document.getElementById('modelSelect').value;

            fetch('/ask', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    prompt: text,
                    model: model,
                    character_id: characterId,
                    temperature: 0.7,
                    user_id: 'web_' + characterId,
                    lang: '{lang}'
                }})
            }})
            .then(r => r.json())
            .then(data => {{
                document.getElementById('status').textContent = '✅ ' + t('response_received', 'Ответ получен');
                if (data.response) {{
                    addMessage('assistant', data.response);
                }} else {{
                    addMessage('assistant', '❌ ' + t('error_prefix', 'Ошибка') + ': ' + (data.error || t('unknown_error', 'Неизвестная ошибка')));
                }}
            }})
            .catch(err => {{
                document.getElementById('status').textContent = '❌ ' + t('connection_error', 'Ошибка соединения');
                addMessage('assistant', '⚠️ ' + t('server_unreachable', 'Не удалось связаться с сервером'));
            }});
        }}

        function addMessage(role, content) {{
            const container = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = 'message ' + role;

            const avatar = document.createElement('div');
            avatar.className = 'avatar-sm';
            avatar.textContent = role === 'user' ? '👤' : '🤖';

            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.textContent = content;

            div.appendChild(avatar);
            div.appendChild(bubble);
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
            messageCount++;
        }}

        document.getElementById('messageInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') sendMessage();
        }});

        fetch('/character/' + characterId)
            .then(r => r.json())
            .then(data => {{
                if (data.history) {{
                    data.history.forEach(msg => {{
                        addMessage(msg.role === 'user' ? 'user' : 'assistant', msg.content);
                    }});
                }}
            }});
    </script>
</body>
</html>
    """

# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI()

# ============================================================
# API ДЛЯ ПЕРСОНАЖЕЙ
# ============================================================

@app.get("/characters")
async def get_characters():
    chars = Character.load_all()
    return {
        "characters": [
            {
                "id": c.id,
                "name": c.name,
                "gender": c.gender,
                "style": c.style,
                "created": c.created,
                "last_used": c.last_used,
                "history_count": len(c.history)
            }
            for c in chars
        ]
    }

@app.get("/character/{character_id}")
async def get_character(character_id: str):
    char = Character.load(character_id)
    if not char:
        return {"error": "Персонаж не найден"}
    return char.to_dict()

@app.post("/character/new")
async def create_character(request: Request):
    try:
        data = await request.json()
        name = data.get("name", "Новый персонаж")
        system_prompt = data.get("system_prompt", "")
        style = data.get("style", "")
        gender = data.get("gender", "male")
        full_system_prompt = SAFETY_PROMPT + "\n\n" + system_prompt
        char = Character(name=name, system_prompt=full_system_prompt, style=style, gender=gender)
        char.save()
        logger.info(f"✅ Создан персонаж: {name} (id: {char.id})")
        return {"id": char.id, "message": f"Персонаж '{name}' создан"}
    except Exception as e:
        logger.error(f"❌ Ошибка создания персонажа: {e}")
        return {"error": str(e)}

@app.post("/character/generate")
async def generate_character(request: Request):
    try:
        data = await request.json()
        description = data.get("description", "")
        if not description or len(description) < 3:
            return {"error": "Описание слишком короткое (минимум 3 символа)"}
        logger.info(f"🎨 Генерация персонажа по описанию: {description}")
        char, error = generate_character_from_description(description)
        if error:
            return {"error": error}
        if char:
            logger.info(f"✅ Сгенерирован персонаж: {char.name} (id: {char.id})")
            return {
                "id": char.id,
                "name": char.name,
                "message": f"Персонаж '{char.name}' создан!",
                "greeting": char.history[0]["content"] if char.history else ""
            }
        else:
            return {"error": "Не удалось сгенерировать персонажа"}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации персонажа: {e}")
        return {"error": str(e)}

@app.get("/chat/{character_id}")
async def chat_page(character_id: str, request: Request):
    char = Character.load(character_id)
    if not char:
        return HTMLResponse("Персонаж не найден", status_code=404)
    
    lang = request.query_params.get("lang", USER_LANG)
    if lang not in ["ru", "en"]:
        lang = "ru"
    
    avatar_html = "🧠"
    if char.avatar_path and os.path.exists(char.avatar_path):
        avatar_html = f'<img src="/avatar/{character_id}/avatar.png">'
    messages_html = ""
    for msg in char.history[-20:]:
        role = "user" if msg["role"] == "user" else "assistant"
        messages_html += f'''
        <div class="message {role}">
            <div class="avatar-sm">{'👤' if role == 'user' else '🤖'}</div>
            <div class="bubble">{msg["content"]}</div>
        </div>
        '''
    return HTMLResponse(generate_chat_html(char, avatar_html, messages_html, lang))

@app.delete("/character/{character_id}")
async def delete_character(character_id: str):
    char = Character.load(character_id)
    if not char:
        return {"error": "Персонаж не найден"}
    filename = os.path.join(CHARACTERS_DIR, f"{character_id}.json")
    if os.path.exists(filename):
        os.remove(filename)
        return {"message": "Персонаж удалён"}
    return {"error": "Персонаж не найден"}

@app.post("/character/memory/clear/{character_id}")
async def clear_character_memory(character_id: str, request: Request):
    data = await request.json()
    user_id = data.get("user_id", "default")
    char = Character.load(character_id)
    if not char:
        return {"error": "Персонаж не найден"}
    if memory_db.clear_history(character_id, user_id):
        return {"message": "Память очищена"}
    return {"error": "Ошибка очистки памяти"}

# ============================================================
# API ДЛЯ КОМНАТ
# ============================================================

@app.get("/rooms")
async def get_rooms():
    rooms = Room.load_all()
    return {
        "rooms": [
            {
                "id": r.id,
                "name": r.name,
                "characters": r.characters,
                "history_count": len(r.history),
                "mode": r.mode,
                "created": r.created
            }
            for r in rooms
        ]
    }

@app.get("/room/{room_id}")
async def get_room(room_id: str):
    room = Room.load(room_id)
    if not room:
        return {"error": "Комната не найдена"}
    return room.to_dict()

@app.post("/room/new")
async def create_room(request: Request):
    data = await request.json()
    name = data.get("name", "Новая комната")
    character_ids = data.get("character_ids", [])
    mode = data.get("mode", "random")
    order = data.get("order", [])
    interrupt = data.get("interrupt", False)
    if len(character_ids) < 2:
        return {"error": "Нужно минимум 2 персонажа"}
    if len(character_ids) > MAX_ROOM_CHARACTERS:
        return {"error": f"Максимум {MAX_ROOM_CHARACTERS} персонажей"}
    try:
        room = Room(name, character_ids, mode, order, interrupt)
        return {"id": room.id, "message": f"Комната '{name}' создана"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/room/{room_id}")
async def delete_room(room_id: str):
    room = Room.load(room_id)
    if not room:
        return {"error": "Комната не найдена"}
    room.delete()
    return {"message": "Комната удалена"}

@app.post("/room/{room_id}/message")
async def add_room_message(room_id: str, request: Request):
    data = await request.json()
    text = data.get("text", "")
    role = data.get("role", "user")
    room = Room.load(room_id)
    if not room:
        return {"error": "Комната не найдена"}
    room.add_message(role, text)
    return {"message": "Сообщение добавлено"}

@app.get("/room/{room_id}/next")
async def get_next_character(room_id: str):
    room = Room.load(room_id)
    if not room:
        return {"error": "Комната не найдена"}
    char = room.get_next_character()
    if not char:
        return {"error": "Нет персонажей"}
    return {"character": char}

# ============================================================
# ОСТАЛЬНЫЕ API (Ollama и т.д.)
# ============================================================

def get_local_ip():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

def is_ollama_running():
    try:
        requests.get("http://localhost:11434/api/tags", timeout=2)
        return True
    except:
        return False

def start_ollama():
    logger.info("🔄 Запуск Ollama...")
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        logger.info("✅ Ollama запущена")
        return True
    except:
        logger.error("❌ Ollama не найдена")
        return False

def ask_ollama(prompt, model="qwen2.5-coder:1.5b", system_prompt="", temperature=0.7):
    try:
        check = requests.get("http://localhost:11434/api/tags", timeout=3)
        if check.status_code != 200:
            return {"error": "Ollama не отвечает"}
    except:
        return {"error": "Ollama не запущена"}
    full_prompt = prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\n{prompt}"
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": temperature
        },
        timeout=120
    )
    if response.status_code == 200:
        result = response.json()
        return {"response": result.get("response", "Нет ответа")}
    else:
        return {"error": f"Ошибка Ollama: {response.status_code}"}

@app.post("/ask")
async def ask(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        model = data.get("model", "qwen2.5-coder:1.5b")
        character_id = data.get("character_id", None)
        temperature = data.get("temperature", 0.7)
        user_id = data.get("user_id", "default")
        system_prompt = ""
        char = None
        if character_id:
            char = Character.load(character_id)
            if char:
                system_prompt = char.system_prompt or ""
                context = char.get_full_context(user_id, limit=30)
                if context:
                    context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context])
                    system_prompt += f"\n\nИстория предыдущих диалогов:\n{context_text}"
        result = ask_ollama(prompt, model, system_prompt, temperature)
        if char and "response" in result and not result.get("error"):
            char.add_message("user", prompt, user_id)
            char.add_message("assistant", result["response"], user_id)
        return result
    except Exception as e:
        logger.error(f"❌ Ошибка в /ask: {e}")
        return {"error": str(e)}

# ============================================================
# ГЛАВНАЯ СТРАНИЦА (С АНИМАЦИЯМИ, СТРЕЛКА СПРАВА, ПЛАВНЫЕ ПОЛЗУНКИ, УЛУЧШЕННЫЙ ШРИФТ)
# ============================================================

@app.get("/")
async def home():
    return HTMLResponse(main_html_template)

# ============================================================
# HTML ТЕМПЛЕЙТ (ОСНОВНОЙ) - С УЛУЧШЕННОЙ ЧИТАЕМОСТЬЮ
# ============================================================

main_html_template = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🧠 NeoBrain</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; padding: 20px; min-height: 100vh; background: #0a0e1a; color: #e8f0ff; }
        .container { max-width: 1200px; margin: 0 auto; }
        
        /* Плавные переходы для всего */
        * { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        
        .header { display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid rgba(0,212,255,0.15); padding-bottom: 15px; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
        .header h1 { font-size: 26px; background: linear-gradient(135deg, #00d4ff, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header-actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
        
        /* Плавные кнопки */
        .btn { 
            padding: 8px 16px; 
            border: none; 
            border-radius: 10px; 
            cursor: pointer; 
            background: rgba(255,255,255,0.06); 
            color: #d4e8ff; 
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important; 
            font-size: 13px; 
        }
        .btn:hover { 
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 30px rgba(0,212,255,0.2);
            background: rgba(255,255,255,0.12);
        }
        .btn-primary { background: #00d4ff; color: #0a0e1a; }
        .btn-primary:hover { background: #00e5ff; box-shadow: 0 8px 30px rgba(0,212,255,0.4); }
        .btn-success { background: #51cf66; color: #0a0e1a; }
        .btn-success:hover { background: #5de07a; box-shadow: 0 8px 30px rgba(81,207,102,0.4); }
        .btn-danger { background: #ff6b6b; color: #0a0e1a; }
        .btn-danger:hover { background: #ff7a7a; box-shadow: 0 8px 30px rgba(255,107,107,0.4); }
        .btn-purple { background: #a855f7; color: #0a0e1a; }
        .btn-purple:hover { background: #b86aff; box-shadow: 0 8px 30px rgba(168,85,247,0.4); }
        .btn-gold { background: #fbbf24; color: #0a0e1a; }
        .btn-gold:hover { background: #fcd34d; box-shadow: 0 8px 30px rgba(251,191,36,0.4); }
        .btn-sm { padding: 4px 10px; font-size: 11px; }
        
        .tabs { display: flex; gap: 4px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab { padding: 10px 24px; border-radius: 12px; cursor: pointer; background: rgba(255,255,255,0.04); color: #8899bb; transition: 0.3s; border: 1px solid transparent; }
        .tab:hover { background: rgba(255,255,255,0.08); transform: translateY(-2px); }
        .tab.active { background: rgba(0,212,255,0.12); color: #00d4ff; border-color: rgba(0,212,255,0.2); }
        
        .content { display: grid; grid-template-columns: 320px 1fr; gap: 20px; }
        @media (max-width: 768px) { .content { grid-template-columns: 1fr; } }
        
        .sidebar { background: rgba(255,255,255,0.02); border-radius: 16px; padding: 16px; border: 1px solid rgba(255,255,255,0.06); max-height: 600px; overflow-y: auto; }
        .sidebar-title { font-size: 14px; font-weight: bold; color: #8899bb; margin-bottom: 12px; letter-spacing: 1px; }
        
        /* Плавные карточки */
        .chat-item { 
            padding: 10px 14px; 
            border-radius: 10px; 
            cursor: pointer; 
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            margin-bottom: 4px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            opacity: 0;
            transform: translateX(-20px);
        }
        .chat-item:hover { 
            transform: translateX(5px);
            background: rgba(255,255,255,0.04);
        }
        .chat-item.active { background: rgba(0,212,255,0.1); border-left: 3px solid #00d4ff; }
        .chat-item .name { font-size: 13px; color: #d4e8ff; }
        .chat-item .badge { font-size: 11px; color: #8899bb; }
        .chat-item .delete-btn { color: #ff6b6b; background: none; border: none; cursor: pointer; font-size: 14px; padding: 0 4px; }
        
        .chat-area { background: rgba(255,255,255,0.02); border-radius: 16px; border: 1px solid rgba(255,255,255,0.06); display: flex; flex-direction: column; min-height: 500px; }
        .chat-header { padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
        .chat-header .title { font-size: 18px; font-weight: bold; color: #d4e8ff; }
        .chat-header .subtitle { font-size: 12px; color: #8899bb; }
        .chat-messages { flex: 1; padding: 16px 20px; overflow-y: auto; max-height: 450px; }
        
        /* Плавные сообщения */
        .message { 
            margin-bottom: 12px; 
            display: flex; 
            align-items: flex-start; 
            gap: 10px; 
            opacity: 0;
            transform: translateY(10px);
            animation: messageIn 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
        }
        @keyframes messageIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user { flex-direction: row-reverse; }
        .message .avatar { width: 36px; height: 36px; border-radius: 50%; background: #2a2a4a; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; border: 1px solid rgba(255,255,255,0.08); }
        .message .bubble { padding: 10px 16px; border-radius: 12px; max-width: 75%; word-break: break-word; font-size: 14px; line-height: 1.5; color: #d4e8ff; }
        .message.user .bubble { background: rgba(0,212,255,0.12); border: 1px solid rgba(0,212,255,0.1); }
        .message.assistant .bubble { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); }
        .message .name-label { font-size: 11px; color: #8899bb; margin-bottom: 2px; }
        
        .chat-input { padding: 16px 20px; border-top: 1px solid rgba(255,255,255,0.06); display: flex; gap: 10px; }
        .chat-input input { flex: 1; padding: 10px 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04); color: #d4e8ff; font-size: 14px; outline: none; }
        .chat-input input:focus { border-color: rgba(0,212,255,0.3); }
        .chat-input input::placeholder { color: #556688; }
        
        /* Плавные модальные окна */
        .modal-overlay { 
            display: none; 
            position: fixed; 
            top: 0; left: 0; right: 0; bottom: 0; 
            background: rgba(0,0,0,0.85); 
            z-index: 9999; 
            justify-content: center; 
            align-items: center; 
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .modal-overlay.active { 
            display: flex !important; 
            opacity: 1;
            animation: modalIn 0.3s ease;
        }
        @keyframes modalIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        .modal { background: #111827; border: 1px solid rgba(0,212,255,0.15); border-radius: 20px; padding: 30px; max-width: 550px; width: 100%; max-height: 90vh; overflow-y: auto; }
        .modal h2 { color: #d4e8ff; margin-bottom: 16px; font-size: 20px; }
        .modal label { display: block; margin-bottom: 4px; font-size: 13px; color: #8899bb; }
        .modal input, .modal select { width: 100%; padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04); color: #d4e8ff; margin-bottom: 12px; }
        .modal .checkbox-group { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 12px; max-height: 150px; overflow-y: auto; }
        .modal .checkbox-group label { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #d4e8ff; cursor: pointer; padding: 4px 8px; border-radius: 6px; transition: 0.2s; }
        .modal .checkbox-group label:hover { background: rgba(255,255,255,0.04); }
        .modal .modal-actions { display: flex; gap: 10px; margin-top: 16px; justify-content: flex-end; }
        
        .empty-state { text-align: center; padding: 40px; color: #8899bb; }
        .empty-state .icon { font-size: 48px; margin-bottom: 12px; }
        
        #status { margin-top: 12px; font-size: 13px; color: #8899bb; text-align: center; }
        
        .room-schema { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-top: 6px; padding: 6px 10px; background: rgba(255,255,255,0.03); border-radius: 8px; }
        .schema-block { padding: 2px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; background: #00d4ff22; color: #00d4ff; border: 1px solid #00d4ff33; }
        .schema-arrow { color: #556688; font-size: 12px; }
        .schema-mode { font-size: 11px; color: #8899bb; margin-left: 6px; }
        
        body.theme-neon { background: #0a0e1a; color: #d4e8ff; }
        body.theme-cyber { background: #0d0a1a; color: #ff66ff; }
        body.theme-matrix { background: #0a0f0a; color: #66ff66; }
        body.theme-ocean { background: #0a1a2a; color: #66ddff; }
        body.theme-sunset { background: #1a0a0a; color: #ffaa88; }
        body.theme-forest { background: #0a1a0a; color: #88ff88; }
        body.theme-cosmos { background: #05050f; color: #cc88ff; }
        body.theme-lava { background: #1a0a05; color: #ff8866; }
        body.theme-gold { background: #1a1a0a; color: #ffdd88; }
        body.theme-purple { background: #0a0a1a; color: #dd88ff; }
        body.theme-cherry { background: #1a0a12; color: #ff88bb; }
        body.theme-emerald { background: #0a1a0a; color: #66ffaa; }
        body.theme-sunny { background: #f5ede1; color: #3a2a1a; }
        body.theme-ice { background: #0a1a2a; color: #88ddff; }
        body.theme-wine { background: #1a0508; color: #ff6677; }
        body.theme-moon { background: #1a1a2a; color: #c8d0e0; }
        body.theme-hightech { background: #0a0a1a; color: #88ddff; }
        body.theme-nature { background: #0a1a0a; color: #88dd88; }
        body.theme-noir { background: #0a0a0a; color: #ddccaa; }
        body.theme-chaos { background: #1a0a1a; color: #ff88ff; }
        body.theme-midnight { background: #050510; color: #aabbdd; }
        body.theme-candy { background: #1a0a1a; color: #ff88dd; }
        body.theme-stealth { background: #0a0a0a; color: #888888; }
        body.theme-aurora { background: #0a1a1a; color: #88ddbb; }
        
        /* ===== КНОПКА-СТРЕЛКА СПРАВА ===== */
        #toggleBtn {
            position: fixed;
            top: 15px;
            right: 20px;
            z-index: 9999;
            background: rgba(0,212,255,0.12);
            border: 1px solid rgba(0,212,255,0.25);
            border-radius: 30px;
            color: #00d4ff;
            font-size: 16px;
            padding: 5px 12px;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: 0 0 20px rgba(0,212,255,0.05);
            backdrop-filter: blur(10px);
            font-weight: bold;
        }
        #toggleBtn:hover {
            background: rgba(0,212,255,0.25);
            box-shadow: 0 0 40px rgba(0,212,255,0.2);
            transform: scale(1.05);
        }
        
        /* ===== ПАНЕЛЬ ===== */
        #panel {
            position: fixed;
            top: -500px;
            right: 20px;
            left: auto;
            transform: none;
            width: 380px;
            max-width: 90vw;
            z-index: 9998;
            background: rgba(10,14,26,0.95);
            border: 1px solid rgba(0,212,255,0.15);
            border-radius: 20px;
            padding: 18px 22px;
            transition: top 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: 0 20px 60px rgba(0,0,0,0.8);
            backdrop-filter: blur(20px);
        }
        #panel.open {
            top: 70px;
        }
        #panel .panel-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
        }
        #panel h4 {
            color: #d4e8ff;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        /* ===== УЛУЧШЕННЫЕ СТИЛИ ДЛЯ SELECT ===== */
        #panel select {
            width: 100%;
            padding: 6px 10px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.04);
            color: #d4e8ff;
            font-size: 12px;
            outline: none;
            font-weight: 600;
        }
        #panel select:focus {
            border-color: rgba(0,212,255,0.3);
        }
        #panel select option {
            background: #0a0e1a;
            padding: 4px 8px;
        }
        
        /* ===== СТИЛИ ДЛЯ МОДЕЛЕЙ (ЦВЕТНЫЕ) ===== */
        #modelSelect {
            font-weight: 700 !important;
            font-size: 13px !important;
            background: rgba(0,212,255,0.08) !important;
            border: 1px solid rgba(0,212,255,0.2) !important;
            color: #ffffff !important;
        }
        #modelSelect option[value="qwen2.5-coder:1.5b"] {
            color: #4ade80 !important;
            font-weight: 600 !important;
        }
        #modelSelect option[value="llama3.2:3b"] {
            color: #60a5fa !important;
            font-weight: 600 !important;
        }
        #modelSelect option[value="mistral:7b"] {
            color: #fbbf24 !important;
            font-weight: 600 !important;
        }
        #modelSelect option[value="llama3.1:8b"] {
            color: #f472b6 !important;
            font-weight: 600 !important;
        }
        
        /* ===== СТИЛИ ДЛЯ ТЕМ ===== */
        #themeSelect {
            font-weight: 600 !important;
            font-size: 13px !important;
        }
        #themeSelect option {
            color: #d4e8ff !important;
        }
        #themeSelect option[value="neon"] { color: #00d4ff !important; }
        #themeSelect option[value="cyber"] { color: #ff44ff !important; }
        #themeSelect option[value="matrix"] { color: #44ff44 !important; }
        #themeSelect option[value="ocean"] { color: #66ddff !important; }
        #themeSelect option[value="sunset"] { color: #ffaa88 !important; }
        #themeSelect option[value="forest"] { color: #88ff88 !important; }
        #themeSelect option[value="cosmos"] { color: #cc88ff !important; }
        #themeSelect option[value="lava"] { color: #ff8866 !important; }
        #themeSelect option[value="gold"] { color: #ffdd88 !important; }
        #themeSelect option[value="purple"] { color: #dd88ff !important; }
        #themeSelect option[value="cherry"] { color: #ff88bb !important; }
        #themeSelect option[value="emerald"] { color: #66ffaa !important; }
        #themeSelect option[value="ice"] { color: #88ddff !important; }
        #themeSelect option[value="wine"] { color: #ff6677 !important; }
        #themeSelect option[value="moon"] { color: #c8d0e0 !important; }
        #themeSelect option[value="hightech"] { color: #88ddff !important; }
        #themeSelect option[value="nature"] { color: #88dd88 !important; }
        #themeSelect option[value="noir"] { color: #ddccaa !important; }
        #themeSelect option[value="chaos"] { color: #ff88ff !important; }
        #themeSelect option[value="midnight"] { color: #aabbdd !important; }
        #themeSelect option[value="candy"] { color: #ff88dd !important; }
        #themeSelect option[value="stealth"] { color: #888888 !important; }
        #themeSelect option[value="aurora"] { color: #88ddbb !important; }
        
        /* ===== СТИЛИ ДЛЯ ПРОВАЙДЕРОВ ===== */
        #providerSelect {
            font-weight: 600 !important;
            font-size: 13px !important;
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            color: #e8f0ff !important;
        }
        #providerSelect option {
            background: #0a0e1a !important;
            color: #e8f0ff !important;
        }
        
        /* ===== СТИЛИ ДЛЯ ПОЛЗУНКОВ ===== */
        .slider-row {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 4px;
            padding: 4px 6px;
            border-radius: 8px;
            background: rgba(255,255,255,0.02);
            transition: all 0.3s ease;
        }
        .slider-row:hover {
            background: rgba(255,255,255,0.06);
        }
        .slider-icon {
            font-size: 14px;
            min-width: 24px;
        }
        .slider-label {
            font-size: 11px;
            color: #8899bb;
            min-width: 82px;
            font-weight: 500;
        }
        .slider-value {
            font-size: 12px;
            color: #00d4ff;
            min-width: 28px;
            text-align: center;
            font-weight: bold;
            transition: color 0.3s ease;
        }
        .slider-row input[type="range"] {
            flex: 1;
            height: 4px;
            -webkit-appearance: none;
            appearance: none;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            outline: none;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .slider-row input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: 0 0 15px rgba(0,212,255,0.3);
        }
        .slider-row input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.2);
        }
        .slider-row input[type="range"]::-moz-range-thumb {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        #cringeSlider::-webkit-slider-thumb {
            background: #ff44ff;
            box-shadow: 0 0 15px rgba(255,68,255,0.4);
        }
        #cringeSlider::-moz-range-thumb {
            background: #ff44ff;
        }
        #temperatureSlider::-webkit-slider-thumb {
            background: #00d4ff;
            box-shadow: 0 0 15px rgba(0,212,255,0.4);
        }
        #temperatureSlider::-moz-range-thumb {
            background: #00d4ff;
        }
        .slider-row input[type="range"]:hover {
            background: rgba(255,255,255,0.2);
        }
        
        /* ===== КНОПКИ В ПАНЕЛИ ===== */
        #panel .row {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }
        #panel .row span {
            font-size: 12px;
            color: #8899bb;
            min-width: 30px;
        }
        #panel .btn-sm {
            padding: 4px 10px;
            font-size: 11px;
        }
        #panel .char-list {
            max-height: 120px;
            overflow-y: auto;
            font-size: 12px;
        }
        #panel .char-list div {
            padding: 4px 8px;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            color: #d4e8ff;
        }
        #panel .char-list div:hover {
            background: rgba(255,255,255,0.04);
        }
        #panel .char-list .del {
            color: #ff6b6b;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Кнопка-стрелка (справа вверху) -->
        <button id="toggleBtn" onclick="togglePanel()">
            <span id="arrowIcon">⚙️</span>
        </button>

        <!-- Плавная выезжающая панель (справа) -->
        <div id="panel">
            <div class="panel-grid">
                <div>
                    <h4>👤 Персонажи</h4>
                    <div class="row">
                        <select id="charSelect" style="flex:1;"></select>
                        <button class="btn btn-sm btn-danger" onclick="deleteCurrentCharacter()">🗑</button>
                    </div>
                    <div class="char-list" id="charList"></div>
                </div>
                <div>
                    <h4>⚙️ Настройки</h4>
                    <div class="row">
                        <span style="min-width:30px;">🤖</span>
                        <select id="providerSelect" style="flex:1;">
                            <option value="ollama">Ollama</option>
                            <option value="openai">OpenAI</option>
                            <option value="gemini">Gemini</option>
                            <option value="claude">Claude</option>
                        </select>
                    </div>
                    <div class="row">
                        <span style="min-width:30px;">📦</span>
                        <select id="modelSelect" style="flex:1;">
                            <option value="qwen2.5-coder:1.5b">⚡ 1.5B (Быстрая)</option>
                            <option value="llama3.2:3b">⚡ 3B (Средняя)</option>
                            <option value="mistral:7b">⚡ 7B (Умная)</option>
                            <option value="llama3.1:8b">⚡ 8B (Тяжёлая)</option>
                        </select>
                    </div>
                    <div class="row">
                        <span style="min-width:30px;">🎨</span>
                        <select id="themeSelect" style="flex:1;">
                            <option value="neon">💠 Неон</option>
                            <option value="cyber">🌀 Киберпанк</option>
                            <option value="matrix">💚 Матрица</option>
                            <option value="ocean">🌊 Океан</option>
                            <option value="sunset">🌅 Закат</option>
                            <option value="forest">🌳 Лес</option>
                            <option value="cosmos">🌠 Космос</option>
                            <option value="lava">🌋 Лава</option>
                            <option value="gold">✨ Золото</option>
                            <option value="purple">🟣 Пурпур</option>
                            <option value="cherry">🌸 Вишня</option>
                            <option value="emerald">💎 Изумруд</option>
                            <option value="sunny">☀️ Солнечная</option>
                            <option value="ice">❄️ Лёд</option>
                            <option value="wine">🍷 Вино</option>
                            <option value="moon">🌙 Лунная</option>
                            <option value="hightech">🧊 Хай-тек</option>
                            <option value="nature">🌿 Природа</option>
                            <option value="noir">🕶️ Нуар</option>
                            <option value="chaos">🌀 Хаос</option>
                            <option value="midnight">🌙 Полночь</option>
                            <option value="candy">🍬 Конфетка</option>
                            <option value="stealth">🥷 Стелс</option>
                            <option value="aurora">🌌 Аврора</option>
                        </select>
                    </div>
                    
                    <!-- Ползунки -->
                    <div class="slider-row">
                        <span class="slider-icon">😬</span>
                        <span class="slider-label">Кринжометр</span>
                        <span class="slider-value" id="cringeLabel">5.0</span>
                        <input type="range" id="cringeSlider" min="0" max="10" value="5" step="0.5">
                    </div>
                    <div class="slider-row">
                        <span class="slider-icon">🌡️</span>
                        <span class="slider-label">Температура</span>
                        <span class="slider-value" id="temperatureLabel">5.0</span>
                        <input type="range" id="temperatureSlider" min="0" max="10" value="5" step="0.5">
                    </div>
                </div>
            </div>
        </div>

        <header class="header">
            <h1 id="appTitle">🧠 NeoBrain</h1>
            <div class="header-actions">
                <button class="btn btn-success" onclick="showCreateCharacterDialog()">➕ Персонаж</button>
                <button class="btn btn-gold" onclick="showGenerateCharacterDialog()">✨ Создать по описанию</button>
                <button class="btn btn-purple" onclick="showCreateRoom()">🏠 Комната</button>
                <button class="btn btn-primary" onclick="openChatPage()">🔗 Открыть в браузере</button>
                <button class="btn" onclick="loadData()">🔄 Обновить</button>
                <button class="btn" onclick="openShareModal()">📤</button>
            </div>
        </header>

        <div class="content">
            <div class="sidebar" id="sidebar">
                <div class="sidebar-title" id="sidebarTitle">📋 Список персонажей</div>
                <div id="sidebarList"></div>
            </div>
            <div class="chat-area">
                <div class="chat-header">
                    <span class="title" id="chatTitle">Выберите чат</span>
                    <span class="subtitle" id="chatSubtitle">Нажмите на элемент слева</span>
                </div>
                <div class="chat-messages" id="chatMessages"></div>
                <div class="chat-input">
                    <input type="text" id="messageInput" placeholder="Напишите сообщение..." disabled>
                    <button class="btn btn-primary" id="sendBtn" disabled>Отправить</button>
                </div>
            </div>
        </div>
        
        <div id="status">Готов к работе...</div>
    </div>

    <!-- Модальные окна -->
    <div class="modal-overlay" id="charModal">
        <div class="modal">
            <h2>✦ Новый персонаж</h2>
            <label>Имя:</label>
            <input type="text" id="charName" placeholder="Введите имя...">
            <label>Описание/характер:</label>
            <input type="text" id="charStyle" placeholder="Весёлый, серьёзный, добрый...">
            <label>System prompt:</label>
            <input type="text" id="charPrompt" placeholder="Ты — полезный AI-помощник...">
            <div class="modal-actions">
                <button class="btn" onclick="closeModal('charModal')">Отмена</button>
                <button class="btn btn-success" onclick="createCharacter()">✅ Создать</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="generateModal">
        <div class="modal">
            <h2>✨ Создать персонажа по описанию</h2>
            <label>Опишите персонажа:</label>
            <input type="text" id="generateDescription" placeholder="Весёлый кот-философ, который любит рассуждать о жизни...">
            <div style="font-size:12px; color:#8899bb; margin-bottom:12px;">
                💡 Примеры: "Мудрый старец", "Весёлый робот", "Добрый собеседник"
            </div>
            <div class="modal-actions">
                <button class="btn" onclick="closeModal('generateModal')">Отмена</button>
                <button class="btn btn-gold" onclick="generateCharacter()">✨ Сгенерировать</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="roomModal">
        <div class="modal">
            <h2>🏠 Создание комнаты</h2>
            <label>Название комнаты:</label>
            <input type="text" id="roomName" placeholder="Введите название...">
            <label>Выберите персонажей (2-10):</label>
            <div class="checkbox-group" id="roomChars"></div>
            <label>Режим ответов:</label>
            <select id="roomMode">
                <option value="random">🎲 Случайный</option>
                <option value="strict">🎯 Строгий</option>
                <option value="interrupt">💬 Перебивание</option>
            </select>
            <label>Схема (для строгого режима, через →):</label>
            <input type="text" id="roomOrder" placeholder="Например: П1→П2→П3">
            <div class="modal-actions">
                <button class="btn" onclick="closeModal('roomModal')">Отмена</button>
                <button class="btn btn-purple" onclick="createRoom()">🏠 Создать</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="shareModal" onclick="if(event.target===this) closeShareModal()">
        <div class="modal">
            <h2>📤 Поделиться доступом</h2>
            <p style="color:#8899bb; margin-bottom:10px;">Отправь эту ссылку друзьям в одной сети:</p>
            <div style="display:flex; gap:10px; margin-bottom:16px;">
                <span id="shareLinkText" style="flex:1; padding:8px 12px; border-radius:8px; background:rgba(255,255,255,0.04); color:#d4e8ff; word-break:break-all;">Загрузка...</span>
                <button class="btn btn-primary" onclick="copyShareLink()">Копировать</button>
            </div>
            <div style="display:flex; justify-content:flex-end;">
                <button class="btn" onclick="closeShareModal()">Закрыть</button>
            </div>
        </div>
    </div>

    <script>
        // ============================================================
        // ПЛАВНАЯ ПАНЕЛЬ (СПРАВА)
        // ============================================================
        var panelOpen = false;

        function togglePanel() {
            var panel = document.getElementById('panel');
            var arrow = document.getElementById('arrowIcon');
            
            if (panelOpen) {
                panel.classList.remove('open');
                arrow.textContent = '⚙️';
                panelOpen = false;
            } else {
                panel.classList.add('open');
                arrow.textContent = '✖';
                panelOpen = true;
            }
        }

        // Автоматически скрываем панель при клике вне её
        document.addEventListener('click', function(e) {
            var panel = document.getElementById('panel');
            var toggleBtn = document.getElementById('toggleBtn');
            if (panelOpen && !panel.contains(e.target) && !toggleBtn.contains(e.target)) {
                togglePanel();
            }
        });

        // ============================================================
        // ПЛАВНЫЕ ПОЛЗУНКИ
        // ============================================================
        function initSliders() {
            var cringeSlider = document.getElementById('cringeSlider');
            var cringeLabel = document.getElementById('cringeLabel');
            if (cringeSlider && cringeLabel) {
                cringeSlider.addEventListener('input', function() {
                    var val = parseFloat(this.value).toFixed(1);
                    cringeLabel.textContent = val;
                    var intensity = val / 10;
                    var r = 255;
                    var g = Math.round(68 + (255 - 68) * (1 - intensity));
                    var b = Math.round(68 + (255 - 68) * (1 - intensity));
                    cringeLabel.style.color = 'rgb(' + r + ',' + g + ',' + b + ')';
                });
                cringeSlider.dispatchEvent(new Event('input'));
            }

            var tempSlider = document.getElementById('temperatureSlider');
            var tempLabel = document.getElementById('temperatureLabel');
            if (tempSlider && tempLabel) {
                tempSlider.addEventListener('input', function() {
                    var val = parseFloat(this.value).toFixed(1);
                    tempLabel.textContent = val;
                    var intensity = val / 10;
                    var r = Math.round(0 + 212 * intensity);
                    var g = Math.round(212 * (1 - intensity));
                    var b = Math.round(255 * (1 - intensity * 0.5));
                    tempLabel.style.color = 'rgb(' + r + ',' + g + ',' + b + ')';
                });
                tempSlider.dispatchEvent(new Event('input'));
            }
        }

        // ============================================================
        // ПЛАВНОЕ ПОЯВЛЕНИЕ КАРТОЧЕК
        // ============================================================
        function animateCards() {
            var items = document.querySelectorAll('.chat-item');
            items.forEach(function(item, index) {
                item.style.opacity = '0';
                item.style.transform = 'translateX(-20px)';
                item.style.transition = 'all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                setTimeout(function() {
                    item.style.opacity = '1';
                    item.style.transform = 'translateX(0)';
                }, 100 + index * 80);
            });
        }

        // ============================================================
        // ОСНОВНЫЕ ФУНКЦИИ
        // ============================================================
        var currentId = null;
        var currentType = null;
        var characters = [];
        var rooms = [];

        function showModal(id) {
            var el = document.getElementById(id);
            if (el) {
                el.classList.add('active');
                el.style.display = 'flex';
            }
        }

        function closeModal(id) {
            var el = document.getElementById(id);
            if (el) {
                el.classList.remove('active');
                setTimeout(function() { el.style.display = 'none'; }, 300);
            }
        }

        function closeShareModal() {
            var el = document.getElementById('shareModal');
            if (el) {
                el.classList.remove('active');
                setTimeout(function() { el.style.display = 'none'; }, 300);
            }
        }

        function openShareModal() {
            var el = document.getElementById('shareModal');
            if (el) {
                el.style.display = 'flex';
                setTimeout(function() { el.classList.add('active'); }, 10);
            }
            fetch('/get_ip')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var linkEl = document.getElementById('shareLinkText');
                    if (linkEl) linkEl.textContent = 'http://' + data.ip + ':8000';
                })
                .catch(function() {
                    var linkEl = document.getElementById('shareLinkText');
                    if (linkEl) linkEl.textContent = 'Не удалось получить IP';
                });
        }

        function copyShareLink() {
            var textEl = document.getElementById('shareLinkText');
            if (!textEl) return;
            var text = textEl.textContent;
            navigator.clipboard.writeText(text)
                .then(function() { alert('Ссылка скопирована!'); })
                .catch(function() { alert('Не удалось скопировать ссылку'); });
        }

        function openChatPage() {
            if (!currentId) {
                alert('Сначала выберите персонажа!');
                return;
            }
            var url = '/chat/' + currentId;
            window.open(url, '_blank');
        }

        function loadData() {
            var statusEl = document.getElementById('status');
            if (statusEl) statusEl.textContent = '⏳ Загрузка...';
            
            Promise.all([
                fetch('/characters').then(function(r) { 
                    if (!r.ok) throw new Error('Ошибка сервера: ' + r.status);
                    return r.json(); 
                }),
                fetch('/rooms').then(function(r) { 
                    if (!r.ok) throw new Error('Ошибка сервера: ' + r.status);
                    return r.json(); 
                })
            ])
            .then(function(data) {
                var charData = data[0];
                var roomData = data[1];
                characters = charData.characters || [];
                rooms = roomData.rooms || [];
                renderAll();
                if (characters.length > 0 && !currentId) {
                    selectCharacter(characters[0].id);
                }
                if (statusEl) statusEl.textContent = '✅ Данные обновлены';
            })
            .catch(function(error) {
                if (statusEl) statusEl.textContent = '❌ Ошибка: ' + error.message;
                alert('Ошибка загрузки: ' + error.message + '\n\nУбедитесь, что сервер запущен (http://localhost:8000)');
            });
        }

        function renderAll() {
            renderSidebar();
            renderCharSelect();
            renderCharList();
        }

        function renderSidebar() {
            var list = document.getElementById('sidebarList');
            if (!list) return;
            list.innerHTML = '';

            var activeTab = document.querySelector('.tab.active');
            var tab = activeTab ? activeTab.dataset.tab : 'characters';
            var items = tab === 'characters' ? characters : rooms;

            if (!items || items.length === 0) {
                list.innerHTML = '<div class="empty-state"><div class="icon">📭</div><div>Нет ' + (tab === 'characters' ? 'персонажей' : 'комнат') + '</div></div>';
                return;
            }

            items.forEach(function(item) {
                var div = document.createElement('div');
                div.className = 'chat-item' + (currentId === item.id ? ' active' : '');

                var nameSpan = document.createElement('span');
                nameSpan.className = 'name';
                if (tab === 'characters') {
                    nameSpan.textContent = '👤 ' + item.name;
                } else {
                    var charNames = (item.characters || []).map(function(c) { return c.name; }).join(', ');
                    nameSpan.textContent = '🏠 ' + item.name + ' (' + charNames + ')';
                }
                div.appendChild(nameSpan);

                var actions = document.createElement('div');
                actions.style.display = 'flex';
                actions.style.alignItems = 'center';
                actions.style.gap = '6px';

                var badge = document.createElement('span');
                badge.className = 'badge';
                badge.textContent = item.history_count || 0;
                actions.appendChild(badge);

                var delBtn = document.createElement('button');
                delBtn.className = 'delete-btn';
                delBtn.textContent = '✕';
                delBtn.onclick = function(e) {
                    e.stopPropagation();
                    if (confirm('Удалить?')) {
                        var url = tab === 'characters' ? '/character/' + item.id : '/room/' + item.id;
                        fetch(url, { method: 'DELETE' })
                            .then(function() {
                                if (currentId === item.id) {
                                    currentId = null;
                                    clearChat();
                                }
                                loadData();
                            });
                    }
                };
                actions.appendChild(delBtn);

                div.appendChild(actions);
                div.onclick = function() {
                    if (tab === 'characters') {
                        openCharacter(item.id);
                    } else {
                        openRoom(item.id);
                    }
                };

                list.appendChild(div);
            });
            
            animateCards();
        }

        function renderCharSelect() {
            var select = document.getElementById('charSelect');
            if (!select) return;
            select.innerHTML = '';

            if (!characters || characters.length === 0) {
                var opt = document.createElement('option');
                opt.textContent = 'Нет персонажей';
                select.appendChild(opt);
                return;
            }

            characters.forEach(function(char) {
                var opt = document.createElement('option');
                opt.value = char.id;
                opt.textContent = char.name + (char.gender === 'female' ? ' ♀' : ' ♂');
                select.appendChild(opt);
            });

            if (currentId) {
                select.value = currentId;
            } else if (characters.length > 0) {
                select.value = characters[0].id;
            }

            select.onchange = function() {
                if (this.value) {
                    selectCharacter(this.value);
                }
            };
        }

        function renderCharList() {
            var container = document.getElementById('charList');
            if (!container) return;
            container.innerHTML = '';

            if (!characters || characters.length === 0) {
                container.innerHTML = '<div style="color:#8899bb; padding:10px; text-align:center;">Нет персонажей</div>';
                return;
            }

            characters.forEach(function(char) {
                var div = document.createElement('div');
                div.className = 'char-item';
                div.style.cssText = 'display:flex; justify-content:space-between; padding:4px 8px; border-radius:6px; color:#d4e8ff; cursor:pointer; font-size:12px;';
                div.onclick = function() { selectCharacter(char.id); };

                var span = document.createElement('span');
                span.textContent = char.name + ' (' + char.history_count + ' сообщ.)';

                var deleteBtn = document.createElement('button');
                deleteBtn.className = 'del';
                deleteBtn.textContent = '✕';
                deleteBtn.onclick = function(e) {
                    e.stopPropagation();
                    if (confirm('Удалить персонажа "' + char.name + '"?')) {
                        fetch('/character/' + char.id, { method: 'DELETE' })
                            .then(function() {
                                if (currentId === char.id) {
                                    currentId = null;
                                    clearChat();
                                }
                                loadData();
                            });
                    }
                };

                div.appendChild(span);
                div.appendChild(deleteBtn);
                container.appendChild(div);
            });
        }

        // Остальные функции
        function showCreateCharacterDialog() {
            document.getElementById('charName').value = '';
            document.getElementById('charStyle').value = '';
            document.getElementById('charPrompt').value = 'Ты — полезный и дружелюбный AI-помощник.';
            showModal('charModal');
        }

        function createCharacter() {
            var statusEl = document.getElementById('status');
            var name = document.getElementById('charName').value.trim();
            var style = document.getElementById('charStyle').value.trim();
            var system_prompt = document.getElementById('charPrompt').value.trim();
            
            if (!name) {
                alert('Введите имя персонажа!');
                return;
            }

            statusEl.textContent = '⏳ Создание персонажа...';

            fetch('/character/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name,
                    style: style,
                    system_prompt: system_prompt
                })
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.error) {
                    statusEl.textContent = '❌ Ошибка: ' + data.error;
                    alert('Ошибка: ' + data.error);
                    return;
                }
                closeModal('charModal');
                loadData();
                statusEl.textContent = '✅ Персонаж "' + name + '" создан!';
            })
            .catch(function(error) {
                statusEl.textContent = '❌ Ошибка: ' + error.message;
                alert('Ошибка при создании персонажа: ' + error.message);
            });
        }

        function showGenerateCharacterDialog() {
            document.getElementById('generateDescription').value = '';
            showModal('generateModal');
        }

        function generateCharacter() {
            var statusEl = document.getElementById('status');
            var description = document.getElementById('generateDescription').value.trim();
            
            if (!description || description.length < 3) {
                alert('Введите описание персонажа (минимум 3 символа)');
                return;
            }

            statusEl.textContent = '🎨 Генерация персонажа...';

            fetch('/character/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    description: description
                })
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.error) {
                    statusEl.textContent = '❌ Ошибка: ' + data.error;
                    alert('Ошибка: ' + data.error);
                    return;
                }
                closeModal('generateModal');
                loadData();
                statusEl.textContent = '✨ Персонаж "' + data.name + '" создан!';
                if (data.greeting) {
                    alert('✨ Персонаж "' + data.name + '" создан!\n\nПриветствие: ' + data.greeting);
                }
            })
            .catch(function(error) {
                statusEl.textContent = '❌ Ошибка: ' + error.message;
                alert('Ошибка при генерации персонажа: ' + error.message);
            });
        }

        function selectCharacter(id) {
            if (!id) return;
            currentId = id;
            currentType = 'character';
            renderAll();
            loadCharacterHistory(id);
            document.getElementById('status').textContent = '💬 Загрузка...';
        }

        function loadCharacterHistory(id) {
            fetch('/character/' + id)
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var container = document.getElementById('chatContainer');
                    if (!container) return;
                    container.innerHTML = '';
                    if (data.history && data.history.length > 0) {
                        data.history.forEach(function(msg) {
                            addMessageToChat(msg.role, msg.content);
                        });
                    } else {
                        var empty = document.createElement('div');
                        empty.style.cssText = 'text-align:center; padding:20px; color:#8899bb;';
                        empty.textContent = '💬 Начните диалог с персонажем';
                        container.appendChild(empty);
                    }
                    var statusEl = document.getElementById('status');
                    if (statusEl) statusEl.textContent = '💬 ' + data.name;
                })
                .catch(function() {
                    document.getElementById('status').textContent = '❌ Ошибка загрузки истории';
                });
        }

        function deleteCurrentCharacter() {
            if (!currentId) {
                alert('Выберите персонажа');
                return;
            }
            if (!confirm('Удалить персонажа?')) return;
            fetch('/character/' + currentId, { method: 'DELETE' })
                .then(function() {
                    currentId = null;
                    clearChat();
                    loadData();
                });
        }

        function showCreateRoom() {
            fetch('/characters')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var container = document.getElementById('roomChars');
                    if (!container) return;
                    container.innerHTML = '';
                    var chars = data.characters || [];
                    if (chars.length === 0) {
                        container.innerHTML = '<div style="color:#8899bb; padding:10px; text-align:center;">Сначала создайте персонажей!</div>';
                        return;
                    }
                    chars.forEach(function(char) {
                        var label = document.createElement('label');
                        var cb = document.createElement('input');
                        cb.type = 'checkbox';
                        cb.value = char.id;
                        label.appendChild(cb);
                        label.appendChild(document.createTextNode(' ' + char.name));
                        container.appendChild(label);
                    });
                    document.getElementById('roomName').value = 'Комната №' + Date.now().toString().slice(-4);
                    document.getElementById('roomMode').value = 'random';
                    document.getElementById('roomOrder').value = '';
                    showModal('roomModal');
                })
                .catch(function(error) {
                    alert('Ошибка загрузки персонажей: ' + error);
                });
        }

        function createRoom() {
            var name = document.getElementById('roomName').value.trim();
            if (!name) {
                alert('Введите название комнаты!');
                return;
            }

            var checkboxes = document.querySelectorAll('#roomChars input:checked');
            var character_ids = Array.from(checkboxes).map(function(cb) { return cb.value; });

            if (character_ids.length < 2) {
                alert('Выберите минимум 2 персонажа!');
                return;
            }
            if (character_ids.length > 10) {
                alert('Максимум 10 персонажей!');
                return;
            }

            var mode = document.getElementById('roomMode').value;
            var orderText = document.getElementById('roomOrder').value.trim();

            var order = [];
            if (mode === 'strict' && orderText) {
                order = orderText.split('→').map(function(s) { return s.trim(); }).filter(function(s) { return s; });
            }

            fetch('/room/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name,
                    character_ids: character_ids,
                    mode: mode,
                    order: order,
                    interrupt: mode === 'interrupt'
                })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                closeModal('roomModal');
                if (data.error) {
                    alert('Ошибка: ' + data.error);
                    return;
                }
                loadData();
                document.getElementById('status').textContent = '✅ Комната "' + name + '" создана!';
                switchTab('rooms');
            })
            .catch(function(error) {
                alert('Ошибка при создании комнаты: ' + error);
            });
        }

        function openRoom(id) {
            currentId = id;
            currentType = 'room';
            renderSidebar();

            fetch('/room/' + id)
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var charNames = (data.characters || []).map(function(c) { return c.name; }).join(', ');
                    var titleEl = document.getElementById('chatTitle');
                    var subtitleEl = document.getElementById('chatSubtitle');
                    if (titleEl) titleEl.textContent = '🏠 ' + data.name;
                    if (subtitleEl) subtitleEl.textContent = '👥 ' + charNames + ' | Режим: ' + data.mode;

                    var schemaHtml = '';
                    if (data.mode === 'strict' && data.order && data.order.length > 0) {
                        var chars = data.characters || [];
                        schemaHtml = '<div class="room-schema">';
                        data.order.forEach(function(id, i) {
                            var c = chars.find(function(ch) { return ch.id === id; });
                            schemaHtml += '<span class="schema-block">' + (c ? c.name : '?') + '</span>';
                            if (i < data.order.length - 1) {
                                schemaHtml += '<span class="schema-arrow">→</span>';
                            }
                        });
                        schemaHtml += '<span class="schema-arrow">↻</span>';
                        schemaHtml += '</div>';
                    } else if (data.mode === 'random') {
                        schemaHtml = '<div class="room-schema"><span class="schema-mode">🎲 Случайный порядок</span></div>';
                    } else if (data.mode === 'interrupt') {
                        schemaHtml = '<div class="room-schema"><span class="schema-mode">💬 С возможностью перебивания</span></div>';
                    }
                    if (subtitleEl) subtitleEl.innerHTML += schemaHtml;

                    var inputEl = document.getElementById('messageInput');
                    var sendEl = document.getElementById('sendBtn');
                    if (inputEl) inputEl.disabled = false;
                    if (sendEl) sendEl.disabled = false;

                    var messages = document.getElementById('chatMessages');
                    if (!messages) return;
                    messages.innerHTML = '';
                    if (data.history && data.history.length > 0) {
                        data.history.forEach(function(msg) {
                            var name = msg.role === 'user' ? 'Вы' : (data.characters || []).find(function(c) { return c.id === msg.role; })?.name || msg.role;
                            addMessage(msg.role === 'user' ? 'user' : 'assistant', msg.content, name);
                        });
                    } else {
                        var empty = document.createElement('div');
                        empty.style.cssText = 'text-align:center; padding:20px; color:#8899bb;';
                        empty.textContent = '💬 Начните диалог в комнате';
                        messages.appendChild(empty);
                    }

                    document.getElementById('status').textContent = '💬 Комната: ' + data.name;
                });
        }

        function sendToRoom(text) {
            addMessage('user', text, 'Вы');

            fetch('/room/' + currentId + '/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, role: 'user' })
            }).then(function() {
                fetch('/room/' + currentId + '/next')
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        if (data.character) {
                            var char = data.character;
                            document.getElementById('status').textContent = '⏳ ' + char.name + ' думает...';

                            fetch('/ask', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    prompt: 'Ты — ' + char.name + '. Твой характер: ' + (char.personality || 'нейтральный') + '. Ответь на сообщение пользователя, учитывая историю чата. Будь кратким.',
                                    character_id: char.id
                                })
                            })
                            .then(function(r) { return r.json(); })
                            .then(function(res) {
                                if (res.response) {
                                    fetch('/room/' + currentId + '/message', {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'application/json' },
                                        body: JSON.stringify({ text: res.response, role: char.id })
                                    }).then(function() {
                                        addMessage('assistant', res.response, char.name);
                                        document.getElementById('status').textContent = '💬 ' + char.name + ' ответил';
                                        loadData();
                                    });
                                }
                            });
                        }
                    });
            });
        }

        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
            var target = document.querySelector('.tab[data-tab="' + tab + '"]');
            if (target) target.classList.add('active');

            var title = document.getElementById('sidebarTitle');
            if (title) {
                title.textContent = tab === 'characters' ? '📋 Список персонажей' : '🏠 Список комнат';
            }

            renderSidebar();
            clearChat();
            document.getElementById('status').textContent = '✅ Переключено на ' + (tab === 'characters' ? 'персонажей' : 'комнаты');
        }

        function initChat() {
            var container = document.getElementById('chatContainer');
            if (!container) return;
            var welcome = document.createElement('div');
            welcome.style.cssText = 'text-align:center; padding:40px; color:#8899bb;';
            welcome.innerHTML = '<div style="font-size:48px; margin-bottom:12px;">💬</div><div>Выберите персонажа или комнату</div>';
            container.appendChild(welcome);
        }

        function addMessageToChat(role, content) {
            var container = document.getElementById('chatContainer');
            if (!container) return;
            var empty = container.querySelector('.empty-state');
            if (empty) empty.remove();

            var wrapper = document.createElement('div');
            wrapper.className = 'message ' + role;
            wrapper.style.cssText = 'display:flex; align-items:flex-start; gap:10px; margin-bottom:12px;' + (role === 'user' ? ' flex-direction:row-reverse;' : '');

            var avatarDiv = document.createElement('div');
            avatarDiv.className = 'avatar';
            avatarDiv.style.cssText = 'width:36px;height:36px;border-radius:50%;background:#2a2a4a;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;border:1px solid rgba(255,255,255,0.08);';
            avatarDiv.textContent = role === 'user' ? '👤' : '🤖';

            var bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'bubble';
            bubbleDiv.style.cssText = 'padding:10px 16px;border-radius:12px;max-width:75%;word-break:break-word;font-size:14px;line-height:1.5;color:#d4e8ff;' + 
                (role === 'user' ? 'background:rgba(0,212,255,0.12);border:1px solid rgba(0,212,255,0.1);' : 'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);');
            bubbleDiv.textContent = content;

            wrapper.appendChild(avatarDiv);
            wrapper.appendChild(bubbleDiv);
            container.appendChild(wrapper);
            container.scrollTop = container.scrollHeight;
        }

        function addMessage(role, content, name) {
            var container = document.getElementById('chatMessages');
            if (!container) return;
            var empty = container.querySelector('.empty-state');
            if (empty) empty.remove();

            var wrapper = document.createElement('div');
            wrapper.className = 'message ' + role;
            wrapper.style.cssText = 'display:flex; align-items:flex-start; gap:10px; margin-bottom:12px;' + (role === 'user' ? ' flex-direction:row-reverse;' : '');

            var avatarDiv = document.createElement('div');
            avatarDiv.className = 'avatar';
            avatarDiv.style.cssText = 'width:36px;height:36px;border-radius:50%;background:#2a2a4a;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;border:1px solid rgba(255,255,255,0.08);';
            avatarDiv.textContent = role === 'user' ? '👤' : '🤖';

            var bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'bubble';
            bubbleDiv.style.cssText = 'padding:10px 16px;border-radius:12px;max-width:75%;word-break:break-word;font-size:14px;line-height:1.5;color:#d4e8ff;' + 
                (role === 'user' ? 'background:rgba(0,212,255,0.12);border:1px solid rgba(0,212,255,0.1);' : 'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);');

            var nameLabel = document.createElement('div');
            nameLabel.style.cssText = 'font-size:11px;color:#8899bb;margin-bottom:2px;';
            nameLabel.textContent = name || (role === 'user' ? 'Вы' : 'AI');

            var textSpan = document.createElement('div');
            textSpan.textContent = content;

            bubbleDiv.appendChild(nameLabel);
            bubbleDiv.appendChild(textSpan);
            wrapper.appendChild(avatarDiv);
            wrapper.appendChild(bubbleDiv);
            container.appendChild(wrapper);
            container.scrollTop = container.scrollHeight;
        }

        function clearChat() {
            var container = document.getElementById('chatContainer');
            if (!container) return;
            container.innerHTML = '';
            var empty = document.createElement('div');
            empty.className = 'empty-state';
            empty.style.cssText = 'text-align:center; padding:40px; color:#8899bb;';
            empty.innerHTML = '<div style="font-size:48px; margin-bottom:12px;">💬</div><div>Выберите персонажа или комнату</div>';
            container.appendChild(empty);

            var inputEl = document.getElementById('messageInput');
            var sendEl = document.getElementById('sendBtn');
            var titleEl = document.getElementById('chatTitle');
            var subtitleEl = document.getElementById('chatSubtitle');
            if (inputEl) inputEl.disabled = true;
            if (sendEl) sendEl.disabled = true;
            if (titleEl) titleEl.textContent = 'Выберите чат';
            if (subtitleEl) subtitleEl.textContent = 'Нажмите на элемент слева';
        }

        function initMessageSend() {
            var input = document.getElementById('aiInput');
            var sendBtn = document.getElementById('aiSendBtn');

            function sendMessage() {
                if (!input) return;
                var text = input.value.trim();
                if (!text) return;
                if (!currentId) {
                    alert('Сначала создайте или выберите персонажа!');
                    return;
                }

                if (currentType === 'character') {
                    sendToCharacter(text);
                    input.value = '';
                } else if (currentType === 'room') {
                    sendToRoom(text);
                    input.value = '';
                }
            }

            function sendToCharacter(text) {
                addMessageToChat('user', text);

                var modelEl = document.getElementById('modelSelect');
                var tempEl = document.getElementById('temperatureSlider');
                
                var model = modelEl ? modelEl.value : 'qwen2.5-coder:1.5b';
                var temperature = tempEl ? parseFloat(tempEl.value) / 10 : 0.5;

                var thinkingWrapper = document.createElement('div');
                thinkingWrapper.className = 'message assistant';
                thinkingWrapper.style.cssText = 'display:flex; align-items:flex-start; gap:10px; margin-bottom:12px;';

                var thinkingAvatar = document.createElement('div');
                thinkingAvatar.className = 'avatar';
                thinkingAvatar.style.cssText = 'width:36px;height:36px;border-radius:50%;background:#2a2a4a;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;border:1px solid rgba(255,255,255,0.08);';
                thinkingAvatar.textContent = '🤖';

                var thinkingMsg = document.createElement('div');
                thinkingMsg.className = 'bubble';
                thinkingMsg.style.cssText = 'padding:10px 16px;border-radius:12px;max-width:75%;word-break:break-word;font-size:14px;line-height:1.5;color:#d4e8ff;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);';
                thinkingMsg.textContent = 'Думаю...';

                thinkingWrapper.appendChild(thinkingAvatar);
                thinkingWrapper.appendChild(thinkingMsg);
                var container = document.getElementById('chatContainer');
                if (container) container.appendChild(thinkingWrapper);

                fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: text,
                        model: model,
                        temperature: temperature,
                        character_id: currentId
                    })
                })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    thinkingWrapper.remove();
                    if (data.response) {
                        addMessageToChat('assistant', data.response);
                    } else {
                        addMessageToChat('assistant', 'Ошибка: ' + (data.error || 'Неизвестная ошибка'));
                    }
                    loadData();
                })
                .catch(function() {
                    thinkingWrapper.remove();
                    addMessageToChat('assistant', 'Ошибка соединения с сервером');
                });
            }

            if (sendBtn) sendBtn.addEventListener('click', sendMessage);
            if (input) input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        }

        function initThemes() {
            var themeSelect = document.getElementById('themeSelect');
            if (!themeSelect) return;
            var savedTheme = localStorage.getItem('neobrain_theme');
            if (savedTheme) {
                themeSelect.value = savedTheme;
                document.body.className = 'theme-' + savedTheme;
            }
            themeSelect.addEventListener('change', function() {
                document.body.className = 'theme-' + this.value;
                localStorage.setItem('neobrain_theme', this.value);
            });
        }

        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.tab').forEach(function(tab) {
                tab.addEventListener('click', function() {
                    switchTab(this.dataset.tab);
                });
            });

            initChat();
            initThemes();
            initSliders();
            initMessageSend();
            loadData();
        });
    </script>
</body>
</html>
"""

# ============================================================
# ЗАПУСК
# ============================================================

@app.get("/get_ip")
async def get_ip():
    return {"ip": LOCAL_IP}

def run_app():
    logger.info("🔄 Запуск NeoBrain...")
    try:
        is_exe = getattr(sys, 'frozen', False)
        if not is_ollama_running():
            logger.info("🔄 Ollama не запущена, запускаем...")
            try:
                if sys.platform == "win32":
                    subprocess.Popen(
                        ["ollama", "serve"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    subprocess.Popen(
                        ["ollama", "serve"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                time.sleep(3)
                logger.info("✅ Ollama запущена")
            except Exception as e:
                logger.error(f"❌ Ошибка запуска Ollama: {e}")
        else:
            logger.info("✅ Ollama уже запущена")
        if is_exe:
            import webview
            logger.info("🌐 Запуск WebView на http://127.0.0.1:8000")
            webview.create_window('NeoBrain', 'http://127.0.0.1:8000', width=1200, height=800)
            webview.start()
            return
        def run_server():
            try:
                uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
            except Exception as e:
                logger.error(f"❌ Ошибка сервера: {e}")
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)
        try:
            requests.get("http://localhost:8000", timeout=2)
            logger.info("✅ Сервер запущен на http://localhost:8000")
        except:
            logger.error("❌ Сервер не запустился!")
            input("Press Enter to exit...")
            return
        try:
            import webview
        except ImportError:
            logger.error("❌ pywebview не установлен")
            input("Press Enter to exit...")
            return
        logger.info(f"🌐 Запуск WebView на http://{LOCAL_IP}:8000")
        webview.create_window('NeoBrain', 'http://localhost:8000', width=1200, height=800)
        webview.start()
    except KeyboardInterrupt:
        logger.info("🛑 NeoBrain остановлен")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {e}")
        import traceback
        logger.critical(traceback.format_exc())

if __name__ == "__main__":
    run_app()