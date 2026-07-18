# -*- coding: utf-8 -*-
import os
import sys
import io
import json
import requests
import socket
import time
import threading
import webbrowser
import subprocess
import signal
import shutil
import base64
import logging
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import tkinter as tk
from tkinter import messagebox

# ============================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================================

# Создаём папку для логов
os.makedirs("logs", exist_ok=True)

# Цвета для терминала (ANSI)
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

# Кастомный форматтер с цветами
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

# Создаём логгер
logger = logging.getLogger('NeoBrain')
logger.setLevel(logging.DEBUG)

# Формат логов
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)

# Хендлер для файла (все логи)
file_handler = logging.FileHandler(
    os.path.join("logs", f"neobrain_{datetime.now().strftime('%Y%m%d')}.log"),
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Хендлер для терминала (только INFO и выше, с цветами)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(ColoredFormatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
))
logger.addHandler(console_handler)

# Отключаем логи uvicorn (чтобы не мешали)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

logger.info("🚀 NeoBrain запущен")
logger.info(f"📁 Логи сохраняются в: logs/neobrain_{datetime.now().strftime('%Y%m%d')}.log")

# ============================================================
# СИСТЕМА ПЕРСОНАЖЕЙ
# ============================================================

CHARACTERS_DIR = "characters"
AVATARS_DIR = "avatars"
USER_AVATAR_DIR = os.path.join(AVATARS_DIR, "user")

def ensure_directories():
    is_exe = getattr(sys, 'frozen', False)
    if is_exe:
        root = tk.Tk()
        root.withdraw()
        msg = (
            "📁 NeoBrain требует создания папок\n\n"
            "Для работы программы необходимо создать следующие папки:\n"
            f"• {CHARACTERS_DIR}/ — для хранения персонажей\n"
            f"• {AVATARS_DIR}/ — для хранения аватаров\n"
            f"• {USER_AVATAR_DIR}/ — для аватара пользователя\n\n"
            "Продолжить?"
        )
        result = messagebox.askyesno("Создание папок", msg, icon='info')
        root.destroy()
        if not result:
            print("❌ Пользователь отменил создание папок. Выход...")
            sys.exit(0)
    
    os.makedirs(CHARACTERS_DIR, exist_ok=True)
    os.makedirs(AVATARS_DIR, exist_ok=True)
    os.makedirs(USER_AVATAR_DIR, exist_ok=True)
    logger.info(f"✅ Папки созданы: {CHARACTERS_DIR}/, {AVATARS_DIR}/, {USER_AVATAR_DIR}/")

ensure_directories()

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
    
    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        self.last_used = datetime.now().isoformat()
        self.save()
        logger.debug(f"💬 Добавлено сообщение для {self.name} ({role}): {content[:50]}...")
    
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
        logger.debug(f"💾 Персонаж {self.name} сохранён")
    
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
    
    def export_json(self):
        data = self.to_dict()
        if self.avatar_path and os.path.exists(self.avatar_path):
            with open(self.avatar_path, 'rb') as f:
                data["avatar_base64"] = base64.b64encode(f.read()).decode('utf-8')
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def import_json(json_data):
        data = json.loads(json_data)
        char = Character(
            name=data["name"],
            system_prompt=data.get("system_prompt", ""),
            style=data.get("style", ""),
            gender=data.get("gender", "male")
        )
        char.id = data.get("id", datetime.now().strftime("%Y%m%d_%H%M%S"))
        char.history = data.get("history", [])
        char.created = data.get("created", datetime.now().isoformat())
        char.last_used = data.get("last_used", datetime.now().isoformat())
        
        if "avatar_base64" in data:
            try:
                char_avatar_dir = os.path.join(AVATARS_DIR, char.id)
                os.makedirs(char_avatar_dir, exist_ok=True)
                avatar_filename = "avatar.png"
                avatar_path = os.path.join(char_avatar_dir, avatar_filename)
                with open(avatar_path, 'wb') as f:
                    f.write(base64.b64decode(data["avatar_base64"]))
                char.avatar_path = avatar_path
                logger.info(f"✅ Аватар импортирован для {char.name}: {avatar_path}")
            except Exception as e:
                logger.error(f"❌ Ошибка импорта аватара для {char.name}: {e}")
        
        char.save()
        return char

def get_or_create_default_character():
    characters = Character.load_all()
    if characters:
        return characters[0]
    
    default = Character(
        name="Помощник",
        system_prompt="Ты — полезный и дружелюбный AI-помощник.",
        style="вежливый, дружелюбный"
    )
    default.save()
    return default

def get_gender_prompt(gender):
    if gender == "female":
        return "Ты — женщина. Отвечай от женского лица. Используй окончания: поняла, сделала, сказала, пошла, пришла и т.д."
    else:
        return "Ты — мужчина. Отвечай от мужского лица. Используй окончания: понял, сделал, сказал, пошёл, пришёл и т.д."

# ============================================================
# НАСТРОЙКА КОДИРОВКИ
# ============================================================
if sys.platform == "win32":
    try:
        # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
        # sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')
        pass
    except:
        pass

if sys.platform == "win32":
    try:
        os.system("chcp 65001 > nul")
    except:
        pass

app = FastAPI()

# ============================================================
# СЛОВАРЬ СЛЕНГА
# ============================================================
SLANG_FILE = "slang_dict.json"
PENDING_FILE = "pending_words.txt"
LAST_RUN_FILE = "last_run.txt"

def load_slang():
    if os.path.exists(SLANG_FILE):
        try:
            with open(SLANG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_slang(slang):
    with open(SLANG_FILE, 'w', encoding='utf-8') as f:
        json.dump(slang, f, indent=2, ensure_ascii=False)

def add_pending_word(word):
    with open(PENDING_FILE, 'a', encoding='utf-8') as f:
        f.write(word.strip() + "\n")

def get_pending_words():
    if not os.path.exists(PENDING_FILE):
        return []
    with open(PENDING_FILE, 'r', encoding='utf-8') as f:
        return [w.strip() for w in f.readlines() if w.strip()]

def clear_pending():
    if os.path.exists(PENDING_FILE):
        os.remove(PENDING_FILE)

def should_run_agent():
    if not os.path.exists(LAST_RUN_FILE):
        return True
    try:
        with open(LAST_RUN_FILE, 'r') as f:
            last = float(f.read())
        return (time.time() - last) > 2 * 60 * 60
    except:
        return True

def update_last_run():
    with open(LAST_RUN_FILE, 'w') as f:
        f.write(str(time.time()))

slang_dict = load_slang()

# ============================================================
# ФАЙЛЫ ДЛЯ ХРАНЕНИЯ
# ============================================================
HISTORY_FILE = "history.json"
CONFIG_FILE = "neobrain_config.json"

def load_history():
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def get_local_ip():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "api_keys": {"openai": "", "gemini": "", "claude": ""},
            "default_provider": "ollama",
            "server_name": "NeoBrain Server",
            "access_code": ""
        }

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

CONFIG = load_config()

# ============================================================
# АВТОЗАПУСК OLLAMA
# ============================================================
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
    except FileNotFoundError:
        logger.error("❌ Ollama не найдена в системе!")
        print("📥 Скачайте: https://ollama.com")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске Ollama: {e}")
        return False

# ============================================================
# AI ПРОВАЙДЕРЫ
# ============================================================
def ask_ollama(prompt, model, system_prompt="", temperature=0.7):
    try:
        check = requests.get("http://localhost:11434/api/tags", timeout=3)
        if check.status_code != 200:
            logger.warning("⚠️ Ollama не отвечает")
            return {"error": "Ollama не отвечает"}
    except:
        logger.warning("⚠️ Ollama не запущена")
        return {"error": "Ollama не запущена"}

    full_prompt = prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\nЗапрос пользователя: {prompt}"

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
        logger.debug(f"📤 Ответ от Ollama получен")
        return {"response": result.get("response", "Нет ответа")}
    else:
        logger.error(f"❌ Ошибка Ollama: {response.status_code}")
        return {"error": f"Ошибка Ollama: {response.status_code}"}

def ask_openai(prompt, api_key, model="gpt-3.5-turbo", system_prompt="", temperature=0.7):
    if not api_key:
        logger.warning("⚠️ API ключ OpenAI не указан")
        return {"error": "API ключ OpenAI не указан"}
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.debug("📤 Ответ от OpenAI получен")
            return {"response": result["choices"][0]["message"]["content"]}
        else:
            logger.error(f"❌ Ошибка OpenAI: {response.status_code}")
            return {"error": f"Ошибка OpenAI: {response.status_code}"}
    except Exception as e:
        logger.error(f"❌ Ошибка OpenAI: {str(e)}")
        return {"error": f"Ошибка OpenAI: {str(e)}"}

def ask_gemini(prompt, api_key, model="gemini-pro", system_prompt="", temperature=0.7):
    if not api_key:
        logger.warning("⚠️ API ключ Google Gemini не указан")
        return {"error": "API ключ Google Gemini не указан"}
    
    try:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{full_prompt}"
            
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            json={
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": temperature}
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.debug("📤 Ответ от Gemini получен")
            return {"response": result["candidates"][0]["content"]["parts"][0]["text"]}
        else:
            logger.error(f"❌ Ошибка Gemini: {response.status_code}")
            return {"error": f"Ошибка Gemini: {response.status_code}"}
    except Exception as e:
        logger.error(f"❌ Ошибка Gemini: {str(e)}")
        return {"error": f"Ошибка Gemini: {str(e)}"}

def ask_claude(prompt, api_key, model="claude-3-haiku-20240307", system_prompt="", temperature=0.7):
    if not api_key:
        logger.warning("⚠️ API ключ Anthropic Claude не указан")
        return {"error": "API ключ Anthropic Claude не указан"}
    
    try:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{full_prompt}"
            
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "max_tokens": 1024,
                "temperature": temperature,
                "messages": [{"role": "user", "content": full_prompt}]
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.debug("📤 Ответ от Claude получен")
            return {"response": result["content"][0]["text"]}
        else:
            logger.error(f"❌ Ошибка Claude: {response.status_code}")
            return {"error": f"Ошибка Claude: {response.status_code}"}
    except Exception as e:
        logger.error(f"❌ Ошибка Claude: {str(e)}")
        return {"error": f"Ошибка Claude: {str(e)}"}

def process_pending_words():
    pending = get_pending_words()
    if not pending:
        return
    
    logger.info(f"🔄 Обработка {len(pending)} новых слов...")
    
    for word in pending:
        try:
            if word not in slang_dict:
                slang_dict[word] = "Новое слово (ожидает проверки)"
                logger.debug(f"  ➕ Добавлено: {word}")
        except:
            pass
    
    save_slang(slang_dict)
    clear_pending()
    update_last_run()
    logger.info("✅ Словарь обновлён")

# ============================================================
# API ДЛЯ РАБОТЫ С ПЕРСОНАЖАМИ
# ============================================================

@app.get("/characters")
async def get_characters():
    chars = Character.load_all()
    logger.debug(f"📋 Загружено персонажей: {len(chars)}")
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
        logger.warning(f"⚠️ Персонаж не найден: {character_id}")
        return {"error": "Персонаж не найден"}
    return char.to_dict()

@app.post("/character/new")
async def create_character(request: Request):
    data = await request.json()
    name = data.get("name", "Новый персонаж")
    system_prompt = data.get("system_prompt", "")
    style = data.get("style", "")
    gender = data.get("gender", "male")
    
    char = Character(name=name, system_prompt=system_prompt, style=style, gender=gender)
    char.save()
    logger.info(f"✅ Создан персонаж: {name} (id: {char.id})")
    return {"id": char.id, "message": f"Персонаж '{name}' создан"}

@app.delete("/character/{character_id}")
async def delete_character(character_id: str):
    char = Character.load(character_id)
    if not char:
        logger.warning(f"⚠️ Попытка удалить несуществующего персонажа: {character_id}")
        return {"error": "Персонаж не найден"}
    
    # Удаляем папку с аватарами персонажа
    char_avatar_dir = os.path.join(AVATARS_DIR, character_id)
    if os.path.exists(char_avatar_dir):
        shutil.rmtree(char_avatar_dir)
        logger.info(f"🗑️ Папка с аватарами персонажа удалена: {char_avatar_dir}")
    
    filename = os.path.join(CHARACTERS_DIR, f"{character_id}.json")
    if os.path.exists(filename):
        os.remove(filename)
        logger.info(f"🗑️ Персонаж {char.name} удалён")
        return {"message": "Персонаж удалён"}
    return {"error": "Персонаж не найден"}

@app.post("/character/export/{character_id}")
async def export_character(character_id: str):
    char = Character.load(character_id)
    if not char:
        logger.warning(f"⚠️ Попытка экспорта несуществующего персонажа: {character_id}")
        return {"error": "Персонаж не найден"}
    logger.info(f"📤 Экспорт персонажа: {char.name}")
    return {
        "filename": f"{char.name}_{char.id}.json",
        "data": char.export_json()
    }

@app.post("/character/import")
async def import_character(request: Request):
    data = await request.json()
    json_data = data.get("json_data")
    if not json_data:
        logger.warning("⚠️ Попытка импорта без данных")
        return {"error": "Нет данных для импорта"}
    
    try:
        char = Character.import_json(json_data)
        logger.info(f"📥 Импортирован персонаж: {char.name}")
        return {"id": char.id, "message": f"Персонаж '{char.name}' импортирован"}
    except Exception as e:
        logger.error(f"❌ Ошибка импорта персонажа: {e}")
        return {"error": f"Ошибка импорта: {str(e)}"}

# ============================================================
# АВАТАРКИ
# ============================================================

@app.get("/avatar/{character_id}/{filename}")
async def get_avatar(character_id: str, filename: str):
    file_path = os.path.join(AVATARS_DIR, character_id, filename)
    if not os.path.exists(file_path):
        logger.warning(f"⚠️ Аватар не найден: {file_path}")
        return {"error": "Файл не найден"}
    return FileResponse(file_path)

@app.post("/character/{character_id}/avatar")
async def set_character_avatar(character_id: str, request: Request):
    char = Character.load(character_id)
    if not char:
        logger.warning(f"⚠️ Попытка загрузить аватар для несуществующего персонажа: {character_id}")
        return {"error": "Персонаж не найден"}
    
    data = await request.json()
    avatar_base64 = data.get("avatar")
    
    if not avatar_base64:
        char_avatar_dir = os.path.join(AVATARS_DIR, character_id)
        if os.path.exists(char_avatar_dir):
            shutil.rmtree(char_avatar_dir)
            logger.info(f"🗑️ Аватар персонажа {char.name} удалён")
        char.avatar_path = None
        char.save()
        return {"message": "Аватар персонажа удалён"}
    
    try:
        char_avatar_dir = os.path.join(AVATARS_DIR, character_id)
        os.makedirs(char_avatar_dir, exist_ok=True)
        
        avatar_filename = "avatar.png"
        avatar_path = os.path.join(char_avatar_dir, avatar_filename)
        
        image_data = base64.b64decode(avatar_base64)
        with open(avatar_path, 'wb') as f:
            f.write(image_data)
        
        if os.path.exists(avatar_path):
            logger.info(f"✅ Аватар персонажа {char.name} сохранён: {avatar_path}")
            char.avatar_path = avatar_path
            char.save()
            return {
                "message": "Аватар персонажа обновлён",
                "path": f"/avatar/{character_id}/{avatar_filename}"
            }
        else:
            logger.error(f"❌ Ошибка сохранения аватара для {char.name}")
            return {"error": "Ошибка сохранения файла"}
            
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения аватара для {char.name}: {e}")
        return {"error": f"Ошибка: {str(e)}"}

@app.get("/character/{character_id}/avatar")
async def get_character_avatar(character_id: str):
    char_avatar_dir = os.path.join(AVATARS_DIR, character_id)
    avatar_path = os.path.join(char_avatar_dir, "avatar.png")
    
    if not os.path.exists(avatar_path):
        return {"path": None}
    
    return {"path": f"/avatar/{character_id}/avatar.png"}

@app.post("/user/avatar")
async def set_user_avatar(request: Request):
    data = await request.json()
    avatar_base64 = data.get("avatar")
    
    avatar_path = os.path.join(USER_AVATAR_DIR, "avatar.png")
    
    if not avatar_base64:
        if os.path.exists(avatar_path):
            os.remove(avatar_path)
        logger.info("🗑️ Аватар пользователя удалён")
        return {"message": "Аватар пользователя удалён"}
    
    try:
        image_data = base64.b64decode(avatar_base64)
        with open(avatar_path, 'wb') as f:
            f.write(image_data)
        
        if os.path.exists(avatar_path):
            logger.info(f"✅ Аватар пользователя сохранён: {avatar_path}")
            return {"message": "Аватар пользователя обновлён", "path": "/avatar/user/avatar.png"}
        else:
            logger.error("❌ Ошибка сохранения аватара пользователя")
            return {"error": "Ошибка сохранения файла"}
            
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения аватара пользователя: {e}")
        return {"error": f"Ошибка: {str(e)}"}

@app.get("/user/avatar")
async def get_user_avatar():
    avatar_path = os.path.join(USER_AVATAR_DIR, "avatar.png")
    if not os.path.exists(avatar_path):
        return {"path": None}
    return {"path": "/avatar/user/avatar.png"}

# ============================================================
# ОСНОВНЫЕ API
# ============================================================

@app.get("/")
async def home():
    return HTMLResponse(html_template)

@app.get("/get_ip")
async def get_ip():
    return {"ip": LOCAL_IP}

@app.post("/ask")
async def ask(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        provider = data.get("provider", "ollama")
        model = data.get("model", "qwen2.5-coder:1.5b")
        api_key = data.get("api_key", "")
        trendy_mode = data.get('trendy_mode', False)
        cringe_level = data.get('cringe_level', 0)
        temperature_value = data.get('temperature', 5)
        character_id = data.get('character_id', None)
        
        logger.info(f"📩 Запрос: {prompt[:50]}{'...' if len(prompt) > 50 else ''} | provider={provider} | char={character_id}")
        
        system_prompt = ""
        
        char = None
        if character_id:
            char = Character.load(character_id)
            if char:
                system_prompt = char.system_prompt or ""
                system_prompt += " " + get_gender_prompt(char.gender)
                logger.debug(f"👤 Персонаж: {char.name} (пол: {char.gender})")
        
        # Температура (эмоциональность)
        if temperature_value <= 1:
            system_prompt += " Отвечай сухо, по фактам, без эмоций. Без лишних слов."
        elif temperature_value <= 3:
            system_prompt += " Отвечай сдержанно, но дружелюбно."
        elif temperature_value <= 5:
            system_prompt += " Отвечай нейтрально, с лёгкой эмоциональностью."
        elif temperature_value <= 7:
            system_prompt += " Отвечай эмоционально, с чувствами."
        elif temperature_value <= 9:
            system_prompt += " Отвечай очень эмоционально, описывай чувства, детали, атмосферу."
        else:
            system_prompt += " Отвечай максимально эмоционально! Описывай всё подробно, с чувствами, красками, деталями."
        
        # Кринжометр
        if cringe_level <= 1:
            system_prompt += " Отвечай максимально серьёзно, без шуток, без сленга, без эмодзи."
        elif cringe_level <= 3:
            system_prompt += " Отвечай вежливо и дружелюбно, иногда с лёгким юмором."
        elif cringe_level <= 6:
            system_prompt += " Отвечай в разговорном стиле, добавляй немного юмора и иногда используй эмодзи."
        elif cringe_level <= 8:
            system_prompt += " Отвечай с юмором, используй сленг, иногда шути, добавляй эмодзи."
        else:
            system_prompt += " Отвечай максимально кринжово и нелепо! Используй зумерский сленг, капс, много эмодзи, гиперболы. Будь максимально смешным и несерьёзным."
        
        if trendy_mode:
            slang_context = ""
            if slang_dict:
                slang_items = list(slang_dict.items())[:30]
                slang_text = "\n".join([f"- {word}: {meaning}" for word, meaning in slang_items])
                slang_context = f"\n\nАктуальный молодёжный сленг (используй эти слова, если они уместны):\n{slang_text}"
            system_prompt += f" Используй актуальный молодёжный сленг в разговоре.{slang_context}"
        
        for word in prompt.split():
            word_clean = word.strip('.,!?;:')
            if word_clean and len(word_clean) > 1 and word_clean.lower() not in slang_dict:
                add_pending_word(word_clean)
        
        if should_run_agent():
            threading.Thread(target=process_pending_words, daemon=True).start()
        
        if char:
            char.add_message("user", prompt)
        
        temp_value = temperature_value / 10.0
        
        if provider == "ollama":
            result = ask_ollama(prompt, model, system_prompt, temp_value)
        elif provider == "openai":
            result = ask_openai(prompt, api_key, model, system_prompt, temp_value)
        elif provider == "gemini":
            result = ask_gemini(prompt, api_key, model, system_prompt, temp_value)
        elif provider == "claude":
            result = ask_claude(prompt, api_key, model, system_prompt, temp_value)
        else:
            result = {"error": f"Неизвестный провайдер: {provider}"}
            logger.error(f"❌ Неизвестный провайдер: {provider}")
        
        if char and "response" in result and not result.get("error"):
            char.add_message("assistant", result["response"])
            logger.debug(f"💬 Ответ сохранён для {char.name}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка в /ask: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": f"Ошибка: {str(e)}"}

# ============================================================
# HTML ТЕМПЛЕЙТ
# ============================================================
html_template = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NeoBrain</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; padding: 20px; min-height: 100vh; background: #0a0e1a; color: #e8f0ff; }
        .container { max-width: 1000px; margin: 0 auto; }
        .header { display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid rgba(0,212,255,0.15); padding-bottom: 20px; margin-bottom: 20px; }
        .header h1 { font-size: 26px; background: linear-gradient(135deg, #00d4ff, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .btn { padding: 8px 20px; border: none; border-radius: 12px; cursor: pointer; background: rgba(255,255,255,0.04); color: #d4e8ff; transition: 0.3s; }
        .btn:hover { transform: translateY(-2px); filter: brightness(1.1); }
        .btn-primary { background: #00d4ff; color: #0a0e1a; }
        .btn-success { background: #51cf66; color: #0a0e1a; }
        .btn-danger { background: #ff6b6b; color: #0a0e1a; }
        .panel { display: none; background: rgba(0,212,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 20px; margin-bottom: 20px; }
        .panel-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; }
        .panel-row select, .panel-row input { padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04); color: #d4e8ff; }
        .ai-section { padding: 24px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.02); min-height: 500px; }
        #chatContainer { max-height: 400px; overflow-y: auto; padding: 12px; margin-bottom: 12px; }
        .chat-message-wrapper { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 12px; }
        .chat-message-wrapper.user { flex-direction: row-reverse; }
        .chat-message-wrapper .avatar { width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0; overflow: hidden; border: 2px solid rgba(0,212,255,0.2); display: flex; align-items: center; justify-content: center; background: #2a2a4a; }
        .chat-message-wrapper .avatar img { width: 100%; height: 100%; object-fit: cover; object-position: top center; }
        .chat-message-wrapper .avatar .default-avatar { font-size: 22px; }
        .chat-message { padding: 10px 16px; border-radius: 12px; max-width: 75%; word-break: break-word; }
        .chat-message-wrapper.user .chat-message { background: rgba(0,212,255,0.08); border: 1px solid rgba(0,212,255,0.1); }
        .chat-message-wrapper.ai .chat-message { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); }
        .ai-input-group { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 10px; }
        .ai-input-group input { flex: 1; padding: 10px 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04); color: #d4e8ff; }
        .char-item { display: flex; justify-content: space-between; padding: 8px 14px; border-radius: 10px; }
        .char-item:hover { background: rgba(255,255,255,0.06); }
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 9999; justify-content: center; align-items: center; }
        .modal-overlay.active { display: flex; }
        .modal { background: #111827; border: 1px solid rgba(0,212,255,0.15); border-radius: 20px; padding: 40px; max-width: 500px; width: 100%; }
        .switch { position: relative; display: inline-block; width: 44px; height: 24px; }
        .switch input { display: none; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: #444; transition: 0.3s; border-radius: 24px; }
        .slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background: white; transition: 0.3s; border-radius: 50%; }
        input:checked + .slider { background: #00d4ff; }
        input:checked + .slider:before { transform: translateX(20px); }
        #cringeSlider, #temperatureSlider { width: 160px; height: 6px; accent-color: #ff44ff; border-radius: 10px; }
        #temperatureSlider { accent-color: #00d4ff; }
        #charList { max-height: 160px; overflow-y: auto; }
        .badge { font-size: 12px; opacity: 0.5; }
        .avatar-preview { width: 36px; height: 36px; border-radius: 50%; border: 2px solid rgba(0,212,255,0.2); object-fit: cover; object-position: top center; background: #2a2a4a; }
        .avatar-preview-empty { display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: 50%; border: 2px solid rgba(0,212,255,0.2); background: #2a2a4a; font-size: 16px; }
        
        /* ===== ВСЕ 24 ТЕМЫ ===== */
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
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1 id="appTitle">🧠 NeoBrain</h1>
            <div>
                <button class="btn btn-success" onclick="showCreateCharacterDialog()">➕ Новый чат</button>
                <button class="btn" onclick="importCharacter()">📥 Импорт</button>
                <button class="btn" onclick="exportCharacter()">📤 Экспорт</button>
                <button class="btn" id="toggleBtn">⚙️</button>
                <button class="btn" onclick="openShareModal()">📤</button>
            </div>
        </header>

        <div class="panel" id="panel">
            <div class="panel-grid">
                <div>
                    <h4>👤 Персонажи</h4>
                    <div class="panel-row">
                        <select id="charSelect"></select>
                        <button class="btn btn-sm btn-danger" onclick="deleteCurrentCharacter()">🗑</button>
                    </div>
                    <div id="charList"></div>
                    
                    <!-- АВАТАРЫ -->
                    <div class="panel-row" style="margin-top:15px; border-top:1px solid rgba(255,255,255,0.05); padding-top:12px;">
                        <span>🖼️ Аватар</span>
                        <select id="avatarTargetSelect" style="flex:1;">
                            <option value="user">👤 Себе</option>
                            <option value="character">🤖 Компаньону</option>
                        </select>
                        <input type="file" id="avatarInput" accept="image/*" style="display:none">
                        <button class="btn btn-sm" onclick="document.getElementById('avatarInput').click()">Загрузить</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteAvatar()">✖</button>
                    </div>
                    
                    <!-- ПРЕВЬЮ АВАТАРОВ -->
                    <div class="panel-row" style="margin-bottom:0;">
                        <span style="font-size:12px; opacity:0.6;">👤 Вы:</span>
                        <div id="userAvatarPreviewContainer" class="avatar-preview-empty">👤</div>
                        <span style="font-size:12px; opacity:0.6; margin-left:10px;">🤖 Компаньон:</span>
                        <div id="characterAvatarPreviewContainer" class="avatar-preview-empty">🤖</div>
                    </div>
                </div>
                <div>
                    <h4>⚙️ Настройки</h4>
                    <div class="panel-row">
                        <span>🤖</span>
                        <select id="providerSelect">
                            <option value="ollama">Ollama</option>
                            <option value="openai">OpenAI</option>
                            <option value="gemini">Gemini</option>
                            <option value="claude">Claude</option>
                        </select>
                    </div>
                    <div class="panel-row">
                        <span>📦</span>
                        <select id="modelSelect">
                            <option value="qwen2.5-coder:1.5b">1.5b (Быстрая)</option>
                            <option value="llama3.2:3b">3b (Средняя)</option>
                            <option value="mistral:7b">7b (Умная)</option>
                            <option value="llama3.1:8b">8b (Тяжёлая)</option>
                        </select>
                    </div>
                    <div class="panel-row">
                        <span>🎨</span>
                        <select id="themeSelect">
                            <option value="neon">💠 Неон</option><option value="cyber">🌀 Киберпанк</option>
                            <option value="matrix">💚 Матрица</option><option value="ocean">🌊 Океан</option>
                            <option value="sunset">🌅 Закат</option><option value="forest">🌳 Лес</option>
                            <option value="cosmos">🌠 Космос</option><option value="lava">🌋 Лава</option>
                            <option value="gold">✨ Золото</option><option value="purple">🟣 Пурпур</option>
                            <option value="cherry">🌸 Вишня</option><option value="emerald">💎 Изумруд</option>
                            <option value="sunny">☀️ Солнечная</option><option value="ice">❄️ Лёд</option>
                            <option value="wine">🍷 Вино</option><option value="moon">🌙 Лунная</option>
                            <option value="hightech">🧊 Хай-тек</option><option value="nature">🌿 Природа</option>
                            <option value="noir">🕶️ Нуар</option><option value="chaos">🌀 Хаос</option>
                            <option value="midnight">🌙 Полночь</option><option value="candy">🍬 Конфетка</option>
                            <option value="stealth">🥷 Стелс</option><option value="aurora">🌌 Аврора</option>
                        </select>
                    </div>
                    <div class="panel-row">
                        <span>🔥 В тренде</span>
                        <label class="switch"><input type="checkbox" id="trendyToggle"><span class="slider"></span></label>
                    </div>
                    <div class="panel-row">
                        <span>😬 Кринжометр</span>
                        <input type="range" id="cringeSlider" min="0" max="10" value="5">
                        <span id="cringeLabel">5</span>
                    </div>
                    <div class="panel-row">
                        <span>🌡️ Температура</span>
                        <input type="range" id="temperatureSlider" min="0" max="10" value="5">
                        <span id="temperatureLabel">5</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="ai-section">
            <div id="chatContainer"></div>
            <div class="ai-input-group">
                <input type="text" id="aiInput" placeholder="Напиши что-нибудь...">
                <button class="btn btn-primary" id="aiSendBtn">Отправить</button>
            </div>
        </div>
        <div id="status">Готов к работе...</div>
    </div>

    <div class="modal-overlay" id="shareModal" onclick="closeModalOutside(event)">
        <div class="modal">
            <h2>Поделиться доступом</h2>
            <p>Отправь эту ссылку друзьям в одной сети:</p>
            <div class="share-link"><span id="shareLinkText">Загрузка...</span>
            <button onclick="copyShareLink()">Копировать</button></div>
            <button class="btn" onclick="closeShareModal()">Закрыть</button>
        </div>
    </div>

    <script>
        // ========================================
        // ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
        // ========================================
        let currentCharId = null;
        let characters = [];

        document.addEventListener('DOMContentLoaded', function() {
            initPanel();
            initChat();
            initProviders();
            initThemes();
            initSliders();
            initMessageSend();
            initAvatarUpload();
            loadAvatars();
            loadCharacters();
        });

        function initPanel() {
            const toggleBtn = document.getElementById('toggleBtn');
            const panel = document.getElementById('panel');
            toggleBtn.addEventListener('click', function() {
                panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
                toggleBtn.textContent = panel.style.display === 'block' ? '▲' : '⚙️';
            });
        }

        function initSliders() {
            const cringeSlider = document.getElementById('cringeSlider');
            const cringeLabel = document.getElementById('cringeLabel');
            cringeSlider.addEventListener('input', function() { cringeLabel.textContent = this.value; });
            
            const tempSlider = document.getElementById('temperatureSlider');
            const tempLabel = document.getElementById('temperatureLabel');
            tempSlider.addEventListener('input', function() { tempLabel.textContent = this.value; });
        }

        function loadCharacters() {
            fetch('/characters')
                .then(r => r.json())
                .then(data => {
                    characters = data.characters || [];
                    renderCharSelect();
                    renderCharList();
                    if (characters.length > 0 && !currentCharId) {
                        selectCharacter(characters[0].id);
                    }
                });
        }

        function renderCharSelect() {
            const select = document.getElementById('charSelect');
            select.innerHTML = '';
            characters.forEach(char => {
                const opt = document.createElement('option');
                opt.value = char.id;
                opt.textContent = char.name + (char.gender === 'female' ? ' ♀' : ' ♂');
                select.appendChild(opt);
            });
            if (currentCharId) select.value = currentCharId;
            select.onchange = function() { selectCharacter(this.value); };
        }

        function renderCharList() {
            const container = document.getElementById('charList');
            container.innerHTML = '';
            characters.forEach(char => {
                const div = document.createElement('div');
                div.className = 'char-item';
                const span = document.createElement('span');
                span.textContent = char.name + ' (' + char.history_count + ' сообщ.)';
                div.appendChild(span);
                container.appendChild(div);
            });
        }

        function selectCharacter(id) {
            console.log('🎯 Выбран персонаж:', id);
            currentCharId = id;
            document.getElementById('charSelect').value = id;
            loadCharacterHistory(id);
            loadAvatars();
        }

        function loadCharacterHistory(id) {
            fetch('/character/' + id)
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('chatContainer');
                    container.innerHTML = '';
                    if (data.history) {
                        data.history.forEach(msg => {
                            addMessageToChat(msg.role, msg.content);
                        });
                    }
                    document.getElementById('status').textContent = '💬 ' + data.name;
                });
        }

        function showCreateCharacterDialog() {
            const name = prompt('👤 Введите имя персонажа:');
            if (!name || !name.trim()) return;
            const gender = confirm('👨 Нажмите OK для мужского пола, Отмена для женского') ? 'male' : 'female';
            
            fetch('/character/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name.trim(), gender: gender })
            })
            .then(() => loadCharacters());
        }

        function deleteCurrentCharacter() {
            if (!currentCharId) return alert('Выберите персонажа');
            if (!confirm('Удалить персонажа?')) return;
            fetch('/character/' + currentCharId, { method: 'DELETE' })
                .then(() => { currentCharId = null; loadCharacters(); });
        }

        function importCharacter() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = function(e) {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = function(ev) {
                    try {
                        const jsonData = ev.target.result;
                        fetch('/character/import', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ json_data: jsonData })
                        })
                        .then(r => r.json())
                        .then(data => {
                            if (data.error) return alert(data.error);
                            alert('✅ Персонаж импортирован!');
                            loadCharacters();
                        });
                    } catch(err) {
                        alert('❌ Ошибка импорта');
                    }
                };
                reader.readAsText(file);
                e.target.value = '';
            };
            input.click();
        }

        function exportCharacter() {
            if (!currentCharId) return alert('Сначала выберите персонажа');
            fetch('/character/export/' + currentCharId, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.error) return alert(data.error);
                    const blob = new Blob([data.data], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = data.filename || 'character.json';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                });
        }

        // ========================================
        // АВАТАРКИ
        // ========================================
        function initAvatarUpload() {
            document.getElementById('avatarInput').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (!file) return;
                
                const target = document.getElementById('avatarTargetSelect').value;
                console.log('🎯 Цель:', target);
                console.log('👤 currentCharId:', currentCharId);
                
                if (target === 'character' && !currentCharId) {
                    alert('❌ Сначала выберите персонажа!');
                    e.target.value = '';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(ev) {
                    const base64 = ev.target.result.split(',')[1];
                    let url = target === 'character' ? '/character/' + currentCharId + '/avatar' : '/user/avatar';
                    
                    console.log('📤 Отправка на:', url);
                    
                    fetch(url, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ avatar: base64 })
                    })
                    .then(r => r.json())
                    .then(data => {
                        console.log('📥 Ответ:', data);
                        if (data.error) return alert('Ошибка: ' + data.error);
                        document.getElementById('status').textContent = '✅ Аватар обновлён!';
                        setTimeout(() => {
                            loadAvatars();
                            refreshAllAvatars();
                        }, 200);
                    })
                    .catch(err => {
                        console.error('❌ Ошибка:', err);
                        alert('Ошибка загрузки');
                    });
                };
                reader.readAsDataURL(file);
                e.target.value = '';
            });
        }

        function refreshAllAvatars() {
            console.log('🔄 Принудительное обновление всех аватаров...');
            loadAvatars();
            
            const allAvatars = document.querySelectorAll('.chat-message-wrapper .avatar');
            console.log('📸 Найдено аватаров в чате:', allAvatars.length);
            
            allAvatars.forEach((el) => {
                const wrapper = el.closest('.chat-message-wrapper');
                if (!wrapper) return;
                const role = wrapper.classList.contains('user') ? 'user' : 'ai';
                const t = Date.now();
                
                if (role === 'user') {
                    fetch('/user/avatar')
                        .then(r => r.json())
                        .then(data => {
                            if (data && data.path) {
                                el.innerHTML = `<img src="${data.path}?t=${t}" style="width:100%;height:100%;object-fit:cover;object-position:top center;">`;
                            } else {
                                el.innerHTML = '<div class="default-avatar">👤</div>';
                            }
                        })
                        .catch(() => el.innerHTML = '<div class="default-avatar">👤</div>');
                } else {
                    if (currentCharId) {
                        fetch('/character/' + currentCharId + '/avatar')
                            .then(r => r.json())
                            .then(data => {
                                if (data && data.path) {
                                    el.innerHTML = `<img src="${data.path}?t=${t}" style="width:100%;height:100%;object-fit:cover;object-position:top center;">`;
                                } else {
                                    el.innerHTML = '<div class="default-avatar">🤖</div>';
                                }
                            })
                            .catch(() => el.innerHTML = '<div class="default-avatar">🤖</div>');
                    }
                }
            });
        }

        function loadAvatars() {
            console.log('🔄 Загрузка аватаров...');
            const t = Date.now();
            
            fetch('/user/avatar')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('userAvatarPreviewContainer');
                    if (data && data.path) {
                        container.innerHTML = `<img src="${data.path}?t=${t}" class="avatar-preview" onerror="this.parentElement.innerHTML='👤';this.parentElement.className='avatar-preview-empty'">`;
                        container.className = '';
                    } else {
                        container.className = 'avatar-preview-empty';
                        container.textContent = '👤';
                    }
                })
                .catch(err => console.error('❌ Ошибка загрузки аватара пользователя:', err));
            
            if (currentCharId) {
                fetch('/character/' + currentCharId + '/avatar')
                    .then(r => r.json())
                    .then(data => {
                        const container = document.getElementById('characterAvatarPreviewContainer');
                        if (data && data.path) {
                            container.innerHTML = `<img src="${data.path}?t=${t}" class="avatar-preview" onerror="this.parentElement.innerHTML='🤖';this.parentElement.className='avatar-preview-empty'">`;
                            container.className = '';
                            console.log('✅ Аватар персонажа загружен:', data.path);
                        } else {
                            container.className = 'avatar-preview-empty';
                            container.textContent = '🤖';
                            console.log('ℹ️ Аватар персонажа отсутствует');
                        }
                    })
                    .catch(err => console.error('❌ Ошибка загрузки аватара персонажа:', err));
            } else {
                const container = document.getElementById('characterAvatarPreviewContainer');
                container.className = 'avatar-preview-empty';
                container.textContent = '🤖';
            }
        }

        function deleteAvatar() {
            const target = document.getElementById('avatarTargetSelect').value;
            if (target === 'character' && !currentCharId) {
                return alert('Сначала выберите персонажа!');
            }
            if (!confirm('Удалить аватар?')) return;
            
            let url = target === 'character' ? '/character/' + currentCharId + '/avatar' : '/user/avatar';
            
            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ avatar: '' })
            })
            .then(() => {
                document.getElementById('status').textContent = '✅ Аватар удалён!';
                setTimeout(() => {
                    loadAvatars();
                    refreshAllAvatars();
                }, 200);
            });
        }

        function initChat() {
            const container = document.getElementById('chatContainer');
            const welcome = document.createElement('div');
            welcome.className = 'chat-message ai';
            welcome.textContent = '💬 Создайте персонажа или импортируйте JSON.';
            container.appendChild(welcome);
        }

        function addMessageToChat(role, content) {
            const container = document.getElementById('chatContainer');
            
            const wrapper = document.createElement('div');
            wrapper.className = 'chat-message-wrapper ' + role;
            
            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'avatar';
            
            const t = Date.now();
            
            if (role === 'user') {
                fetch('/user/avatar')
                    .then(r => r.json())
                    .then(data => {
                        if (data && data.path) {
                            avatarDiv.innerHTML = `<img src="${data.path}?t=${t}" style="width:100%;height:100%;object-fit:cover;object-position:top center;">`;
                        } else {
                            avatarDiv.innerHTML = '<div class="default-avatar">👤</div>';
                        }
                    })
                    .catch(() => avatarDiv.innerHTML = '<div class="default-avatar">👤</div>');
            } else {
                if (currentCharId) {
                    fetch('/character/' + currentCharId + '/avatar')
                        .then(r => r.json())
                        .then(data => {
                            if (data && data.path) {
                                avatarDiv.innerHTML = `<img src="${data.path}?t=${t}" style="width:100%;height:100%;object-fit:cover;object-position:top center;">`;
                            } else {
                                avatarDiv.innerHTML = '<div class="default-avatar">🤖</div>';
                            }
                        })
                        .catch(() => avatarDiv.innerHTML = '<div class="default-avatar">🤖</div>');
                } else {
                    avatarDiv.innerHTML = '<div class="default-avatar">🤖</div>';
                }
            }
            
            const msgDiv = document.createElement('div');
            msgDiv.className = 'chat-message';
            msgDiv.textContent = content;
            
            wrapper.appendChild(avatarDiv);
            wrapper.appendChild(msgDiv);
            container.appendChild(wrapper);
            container.scrollTop = container.scrollHeight;
        }

        function initMessageSend() {
            const input = document.getElementById('aiInput');
            const sendBtn = document.getElementById('aiSendBtn');
            
            function sendMessage() {
                const text = input.value.trim();
                if (!text) return;
                if (!currentCharId) {
                    alert('Сначала создайте или выберите персонажа!');
                    return;
                }
                
                addMessageToChat('user', text);
                input.value = '';
                
                const provider = document.getElementById('providerSelect').value;
                const model = document.getElementById('modelSelect').value;
                const trendy = document.getElementById('trendyToggle').checked;
                const cringe = parseInt(document.getElementById('cringeSlider').value);
                const temperature = parseInt(document.getElementById('temperatureSlider').value);
                
                const thinkingWrapper = document.createElement('div');
                thinkingWrapper.className = 'chat-message-wrapper ai';
                const thinkingAvatar = document.createElement('div');
                thinkingAvatar.className = 'avatar';
                thinkingAvatar.innerHTML = '<div class="default-avatar">🤖</div>';
                const thinkingMsg = document.createElement('div');
                thinkingMsg.className = 'chat-message';
                thinkingMsg.textContent = 'Думаю...';
                thinkingWrapper.appendChild(thinkingAvatar);
                thinkingWrapper.appendChild(thinkingMsg);
                document.getElementById('chatContainer').appendChild(thinkingWrapper);
                
                fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: text,
                        provider: provider,
                        model: model,
                        trendy_mode: trendy,
                        cringe_level: cringe,
                        temperature: temperature,
                        character_id: currentCharId
                    })
                })
                .then(r => r.json())
                .then(data => {
                    thinkingWrapper.remove();
                    addMessageToChat('ai', data.response || 'Ошибка');
                })
                .catch(() => {
                    thinkingWrapper.remove();
                    addMessageToChat('ai', 'Ошибка соединения');
                });
            }
            
            sendBtn.addEventListener('click', sendMessage);
            input.addEventListener('keypress', function(e) { if (e.key === 'Enter') sendMessage(); });
        }

        function initProviders() {
            document.getElementById('providerSelect').addEventListener('change', function() {});
        }

        function initThemes() {
            const themeSelect = document.getElementById('themeSelect');
            const savedTheme = localStorage.getItem('neobrain_theme');
            if (savedTheme) {
                themeSelect.value = savedTheme;
                document.body.className = 'theme-' + savedTheme;
            }
            themeSelect.addEventListener('change', function() {
                document.body.className = 'theme-' + this.value;
                localStorage.setItem('neobrain_theme', this.value);
            });
        }

        function openShareModal() {
            document.getElementById('shareModal').classList.add('active');
            fetch('/get_ip').then(r => r.json()).then(data => {
                document.getElementById('shareLinkText').textContent = 'http://' + data.ip + ':8000';
            });
        }
        function closeShareModal() { document.getElementById('shareModal').classList.remove('active'); }
        function closeModalOutside(e) { if (e.target === e.currentTarget) closeShareModal(); }
        function copyShareLink() {
            const text = document.getElementById('shareLinkText').textContent;
            navigator.clipboard.writeText(text).then(() => alert('Ссылка скопирована!'));
        }
    </script>
</body>
</html>
"""

# ============================================================
# ЗАПУСК
# ============================================================

def run_app():
    logger.info("🔄 Запуск NeoBrain...")
    try:
        is_exe = getattr(sys, 'frozen', False)
        logger.info(f"📦 Режим: {'EXE' if is_exe else 'Python'}")
        
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
            log_file = open("neobrain.log", "w", encoding='utf-8')
            
            def log(msg):
                try:
                    log_file.write(str(msg) + "\n")
                    log_file.flush()
                except:
                    pass
            
            def run_server():
                try:
                    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="critical", access_log=False)
                except Exception as e:
                    log(f"Server error: {e}")
                    logger.error(f"❌ Ошибка сервера: {e}")
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            time.sleep(3)
            
            try:
                import webview
            except ImportError:
                log("ERROR: pywebview not installed")
                logger.error("❌ pywebview не установлен")
                log_file.close()
                return
            
            log_file.close()
            logger.info("🌐 Запуск WebView на http://127.0.0.1:8000")
            webview.create_window('NeoBrain', 'http://127.0.0.1:8000', width=1200, height=800)
            webview.start()
            return
        
        # Проверяем порт
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        if result == 0:
            logger.warning("⚠️ Порт 8000 уже занят!")
            print("WARNING: Port 8000 already in use!")
            input("Press Enter to exit...")
            return

        def run_server():
            try:
                uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
            except Exception as e:
                logger.error(f"❌ Ошибка сервера: {e}")
                print(f"Server error: {e}")

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)

        try:
            requests.get("http://localhost:8000", timeout=2)
            logger.info("✅ Сервер запущен на http://localhost:8000")
            print("Server started!")
        except:
            logger.error("❌ Сервер не запустился!")
            print("Server failed to start!")
            input("Press Enter to exit...")
            return

        try:
            import webview
        except ImportError:
            logger.error("❌ pywebview не установлен")
            print("ERROR: pywebview not installed")
            input("Press Enter to exit...")
            return

        logger.info(f"🌐 Запуск WebView на http://{LOCAL_IP}:8000")
        print("\n" + "=" * 55)
        print("NeoBrain started!")
        print("Opening application window...")
        print(f"Local address: http://{LOCAL_IP}:8000")
        print("Close the window to stop")
        print("=" * 55 + "\n")

        webview.create_window('NeoBrain', 'http://localhost:8000', width=1200, height=800)
        webview.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 NeoBrain остановлен пользователем")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {e}")
        import traceback
        logger.critical(traceback.format_exc())

if __name__ == "__main__":
    run_app()