import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import sys
import subprocess
import math
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageTk
import pywinstyles
import requests
import zipfile
import shutil
import tempfile
import threading
import time
from pathlib import Path

# ============================================================
# НАСТРОЙКА CUSTOMTKINTER
# ============================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ============================================================
# КОНСТАНТЫ
# ============================================================
GITHUB_REPO = "Sbeuvadyarik67/NeoLauncher-"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"
VERSION_FILE = "version.json"
CURRENT_VERSION = "3.1.0"

# ============================================================
# КЛАСС ОБНОВЛЯТОРА
# ============================================================

class Updater:
    def __init__(self, parent):
        self.parent = parent
        self.update_window = None
        self.progress_bar = None
        self.status_label = None
        
    def check_for_updates(self, show_progress=True):
        try:
            if show_progress:
                self.show_update_window()
                self.update_status("🔄 Проверка обновлений...")
            
            response = requests.get(f"{GITHUB_API}/releases/latest", timeout=10)
            
            if response.status_code != 200:
                self.update_status("❌ Не удалось проверить обновления")
                return None
            
            release_data = response.json()
            latest_version = release_data.get("tag_name", "").replace("v", "")
            
            if show_progress:
                self.update_status(f"📡 Версия: {latest_version}")
            
            if latest_version > CURRENT_VERSION:
                return {
                    "version": latest_version,
                    "download_url": release_data.get("zipball_url"),
                    "body": release_data.get("body", "Нет описания изменений"),
                    "created_at": release_data.get("created_at", "")
                }
            else:
                if show_progress:
                    self.update_status("✅ У вас последняя версия!")
                    self.close_update_window()
                return None
                
        except Exception as e:
            self.update_status(f"❌ Ошибка: {str(e)}")
            return None
    
    def download_and_update(self, update_info):
        try:
            self.update_status("📥 Загрузка обновления...")
            
            response = requests.get(update_info["download_url"], stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "update.zip")
            
            downloaded = 0
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        self.update_progress(progress)
            
            self.update_status("📦 Распаковка...")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            extracted_dir = None
            for item in os.listdir(temp_dir):
                if os.path.isdir(os.path.join(temp_dir, item)) and item.startswith("Sbeuvadyarik67-NeoLauncher-"):
                    extracted_dir = os.path.join(temp_dir, item)
                    break
            
            if not extracted_dir:
                raise Exception("Не найдены файлы обновления")
            
            self.update_status("📋 Установка обновления...")
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            files_to_update = []
            
            for root, dirs, files in os.walk(extracted_dir):
                for file in files:
                    if file.endswith('.py') or file == 'manifest.json' or file == 'version.json':
                        rel_path = os.path.relpath(os.path.join(root, file), extracted_dir)
                        files_to_update.append(rel_path)
            
            for rel_path in files_to_update:
                src = os.path.join(extracted_dir, rel_path)
                dst = os.path.join(current_dir, rel_path)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                self.update_status(f"📄 {rel_path}")
            
            version_data = {
                "version": update_info["version"],
                "updated_at": datetime.now().isoformat()
            }
            with open(os.path.join(current_dir, VERSION_FILE), 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)
            
            self.update_status("✅ Обновление установлено!")
            time.sleep(1)
            
            messagebox.showinfo(
                "✅ Обновление установлено",
                f"Обновление до версии {update_info['version']} успешно установлено!\n\n"
                f"Что нового:\n{update_info['body'][:500]}\n\n"
                "Приложение будет перезапущено."
            )
            
            self.restart_app()
            
        except Exception as e:
            self.update_status(f"❌ Ошибка обновления: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось установить обновление:\n{str(e)}")
    
    def show_update_window(self):
        if self.update_window:
            return
            
        self.update_window = ctk.CTkToplevel(self.parent.root)
        self.update_window.title("✦ Обновление ✦")
        self.update_window.geometry("500x200")
        self.update_window.configure(fg_color=self.parent.theme["bg"])
        self.update_window.transient(self.parent.root)
        self.update_window.grab_set()
        
        ctk.CTkLabel(
            self.update_window,
            text="✦ Проверка обновлений",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.parent.theme["text"]
        ).pack(pady=(20, 15))
        
        self.status_label = ctk.CTkLabel(
            self.update_window,
            text="Подготовка...",
            font=ctk.CTkFont(size=12),
            text_color=self.parent.theme["text_secondary"]
        )
        self.status_label.pack(pady=(0, 15))
        
        self.progress_bar = ctk.CTkProgressBar(
            self.update_window,
            width=400,
            height=10,
            corner_radius=5
        )
        self.progress_bar.pack(pady=(0, 20))
        self.progress_bar.set(0)
        
        ctk.CTkButton(
            self.update_window,
            text="Закрыть",
            width=100,
            height=35,
            corner_radius=8,
            fg_color=self.parent.theme["glass"],
            hover_color=self.parent.theme["glass_border"],
            text_color=self.parent.theme["text_secondary"],
            command=self.close_update_window
        ).pack()
    
    def update_status(self, text):
        if self.status_label:
            self.status_label.configure(text=text)
            self.update_window.update()
    
    def update_progress(self, value):
        if self.progress_bar:
            self.progress_bar.set(value / 100)
            self.update_window.update()
    
    def close_update_window(self):
        if self.update_window:
            self.update_window.destroy()
            self.update_window = None
            self.status_label = None
            self.progress_bar = None
    
    def restart_app(self):
        python = sys.executable
        script = os.path.abspath(sys.argv[0])
        subprocess.Popen([python, script])
        self.parent.root.quit()
        self.parent.root.destroy()

# ============================================================
# КЛАСС ДЛЯ УПРАВЛЕНИЯ ПРОЕКТАМИ
# ============================================================

class ProjectManager:
    def __init__(self, parent):
        self.parent = parent
        self.base_dir = parent.base_dir
        self.manifest_path = parent.manifest_path
        self.projects_dir = os.path.join(self.base_dir, "projects")
        
        # Создаём папку projects если её нет
        os.makedirs(self.projects_dir, exist_ok=True)
    
    def add_project(self, file_path):
        try:
            if not os.path.exists(file_path):
                return False, "Файл не найден"
            
            ext = os.path.splitext(file_path)[1].lower()
            file_name = os.path.basename(file_path)
            name = os.path.splitext(file_name)[0]
            
            supported_types = {
                '.py': 'python',
                '.exe': 'exe',
                '.bat': 'bat',
                '.cmd': 'cmd',
                '.url': 'url',
                '.lnk': 'lnk'
            }
            
            if ext not in supported_types:
                return False, f"Неподдерживаемый тип файла: {ext}"
            
            dest_path = os.path.join(self.projects_dir, file_name)
            
            counter = 1
            base_name = name
            while os.path.exists(dest_path):
                new_name = f"{base_name}_{counter}{ext}"
                dest_path = os.path.join(self.projects_dir, new_name)
                counter += 1
            
            shutil.copy2(file_path, dest_path)
            
            icon_map = {
                '.py': '🐍',
                '.exe': '⚙️',
                '.bat': '📜',
                '.cmd': '📜',
                '.url': '🔗',
                '.lnk': '🔗'
            }
            
            color_map = {
                '.py': '#6c5ce7',
                '.exe': '#00b894',
                '.bat': '#fdcb6e',
                '.cmd': '#fdcb6e',
                '.url': '#0984e3',
                '.lnk': '#0984e3'
            }
            
            manifest = self.parent.load_manifest()
            
            project_id = name.lower().replace(' ', '_')
            counter = 1
            original_id = project_id
            while project_id in manifest["projects"]:
                project_id = f"{original_id}_{counter}"
                counter += 1
            
            manifest["projects"][project_id] = {
                "name": name,
                "version": "1.0.0",
                "path": f"projects/{os.path.basename(dest_path)}",
                "icon": icon_map.get(ext, '📦'),
                "color": color_map.get(ext, '#6c5ce7'),
                "description": f"Добавлен вручную: {file_name}",
                "tags": [supported_types[ext].capitalize()],
                "type": supported_types[ext]
            }
            
            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            return True, f"Проект '{name}' добавлен!"
            
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

# ============================================================
# ГЛАВНЫЙ КЛАСС ЛАУНЧЕРА
# ============================================================

class NeoLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("✦ NeoLauncher ✦")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        
        self.root.overrideredirect(True)
        
        # ============================================================
        # ТЕМЫ
        # ============================================================
        self.themes = {
            "nebula": {
                "name": "Туманность",
                "bg": "#0a0a12",
                "surface": "#1a1a3e",
                "surface_hover": "#2a2a5e",
                "glass": "#1a1a3e",
                "glass_border": "#7c3aed",
                "text": "#f0ecff",
                "text_secondary": "#a898cc",
                "accent": "#7c3aed",
                "accent_hover": "#8b5cf6",
                "accent_light": "#a78bfa",
                "gradient1": "#0a0a12",
                "gradient2": "#1a0a30",
                "gradient3": "#2a0a40"
            },
            "aurora": {
                "name": "Северное сияние",
                "bg": "#080e1a",
                "surface": "#0a1a3a",
                "surface_hover": "#1a2a4a",
                "glass": "#0a1a3a",
                "glass_border": "#06b6d4",
                "text": "#d4f4ff",
                "text_secondary": "#7ab8d4",
                "accent": "#06b6d4",
                "accent_hover": "#67e8f9",
                "accent_light": "#7dd3fc",
                "gradient1": "#080e1a",
                "gradient2": "#0a1a2a",
                "gradient3": "#0a2a3a"
            },
            "ember": {
                "name": "Пламя",
                "bg": "#1a0805",
                "surface": "#2a1a0e",
                "surface_hover": "#3a2a1a",
                "glass": "#2a1a0e",
                "glass_border": "#f97316",
                "text": "#ffdcc4",
                "text_secondary": "#cc8a7a",
                "accent": "#f97316",
                "accent_hover": "#fb923c",
                "accent_light": "#fdba74",
                "gradient1": "#1a0805",
                "gradient2": "#2a100a",
                "gradient3": "#3a1a0f"
            },
            "crystal": {
                "name": "Хрусталь",
                "bg": "#080e1a",
                "surface": "#0a2a3a",
                "surface_hover": "#1a3a4a",
                "glass": "#0a2a3a",
                "glass_border": "#22d3ee",
                "text": "#d4f4ff",
                "text_secondary": "#7ab8d4",
                "accent": "#22d3ee",
                "accent_hover": "#67e8f9",
                "accent_light": "#a5f3fc",
                "gradient1": "#080e1a",
                "gradient2": "#0a1a2a",
                "gradient3": "#0a2a3a"
            },
            "royal": {
                "name": "Королевский",
                "bg": "#0a080f",
                "surface": "#1a0a3e",
                "surface_hover": "#2a1a5e",
                "glass": "#1a0a3e",
                "glass_border": "#e879f9",
                "text": "#f0d8ff",
                "text_secondary": "#b888dd",
                "accent": "#e879f9",
                "accent_hover": "#f0abfc",
                "accent_light": "#f8b8fc",
                "gradient1": "#0a080f",
                "gradient2": "#1a0a2e",
                "gradient3": "#2a0a4e"
            }
        }
        
        self.current_theme = "nebula"
        self.theme = self.themes[self.current_theme]
        
        # ============================================================
        # ЗАГРУЗКА ДАННЫХ (СНАЧАЛА!)
        # ============================================================
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.manifest_path = os.path.join(self.base_dir, "manifest.json")
        self.settings_path = os.path.join(self.base_dir, "launcher_settings.json")
        
        self.manifest = self.load_manifest()
        self.settings = self.load_settings()
        
        # ============================================================
        # ПАРАМЕТРЫ (ПОТОМ!)
        # ============================================================
        self.anim_time = 0
        self.flow_particles = []
        self.hover_index = -1
        self.all_projects = {}
        self.search_query = ""
        
        # Updater и ProjectManager создаются ПОСЛЕ загрузки данных
        self.updater = Updater(self)
        self.project_manager = ProjectManager(self)
        
        # ============================================================
        # ПОСТРОЕНИЕ UI
        # ============================================================
        self.setup_ui()
        self.apply_glass_effects()
        self.create_flow_particles()
        self.render_projects()
        
        self.animate()
        self.make_draggable()
        self.fade_in()
        
        self.check_for_updates_background()
    
    # ============================================================
    # ПРОВЕРКА ОБНОВЛЕНИЙ
    # ============================================================
    
    def check_for_updates_background(self):
        def check():
            update_info = self.updater.check_for_updates(show_progress=False)
            if update_info:
                self.root.after(0, lambda: self.show_update_notification(update_info))
        
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
    
    def show_update_notification(self, update_info):
        result = messagebox.askyesno(
            "🔄 Доступно обновление",
            f"Доступна новая версия: v{update_info['version']}\n\n"
            f"Что нового:\n{update_info['body'][:300]}{'...' if len(update_info['body']) > 300 else ''}\n\n"
            "Установить обновление?"
        )
        
        if result:
            def update_thread():
                self.updater.download_and_update(update_info)
            
            thread = threading.Thread(target=update_thread, daemon=True)
            thread.start()
    
    # ============================================================
    # ЗАГРУЗКА ДАННЫХ
    # ============================================================
    
    def load_manifest(self):
        default = {
            "projects": {
                "neobrain": {
                    "name": "NeoBrain",
                    "version": "2.1.2",
                    "path": "projects/neobrain.py",
                    "icon": "🧠",
                    "color": "#7c3aed",
                    "description": "Локальный AI-чат с персонажами",
                    "tags": ["AI", "Chat"],
                    "type": "python"
                },
                "neospace": {
                    "name": "NeoSpace-Pro",
                    "version": "1.0.0",
                    "path": "projects/neospace.py",
                    "icon": "🖥️",
                    "color": "#06b6d4",
                    "description": "Виртуальная среда для экспериментов",
                    "tags": ["Virtual", "Sandbox"],
                    "type": "python"
                },
                "whydoes": {
                    "name": "Why-Does-This-Exist",
                    "version": "1.0.0",
                    "path": "projects/whydoes.py",
                    "icon": "🌀",
                    "color": "#f97316",
                    "description": "Генератор визуального безумия",
                    "tags": ["Visual", "Art"],
                    "type": "python"
                }
            }
        }
        try:
            if os.path.exists(self.manifest_path):
                with open(self.manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(self.manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(default, f, indent=2, ensure_ascii=False)
                return default
        except:
            return default
    
    def load_settings(self):
        default = {"theme": "nebula", "auto_update": True}
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "theme" in data and data["theme"] in self.themes:
                        self.current_theme = data["theme"]
                        self.theme = self.themes[self.current_theme]
                    return data
            else:
                with open(self.settings_path, 'w', encoding='utf-8') as f:
                    json.dump(default, f, indent=2, ensure_ascii=False)
                return default
        except:
            return default
    
    # ============================================================
    # ПОСТРОЕНИЕ UI
    # ============================================================
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.theme["bg"],
            corner_radius=0
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.bg_canvas = tk.Canvas(
            self.main_frame,
            bg=self.theme["bg"],
            highlightthickness=0,
            bd=0
        )
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.create_background()
        
        # ============================================================
        # ВЕРХНЯЯ ПАНЕЛЬ
        # ============================================================
        self.nav_panel = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["glass"],
            corner_radius=16,
            width=int(self.root.winfo_width() * 0.96),
            height=75
        )
        self.nav_panel.place(relx=0.02, rely=0.02)
        
        logo_frame = ctk.CTkFrame(
            self.nav_panel,
            fg_color="transparent"
        )
        logo_frame.place(relx=0.03, rely=0.5, anchor=tk.W)
        
        self.logo = ctk.CTkLabel(
            logo_frame,
            text="✦ NeoLauncher",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.theme["text"]
        )
        self.logo.pack(side=tk.LEFT)
        
        version_frame = ctk.CTkFrame(
            logo_frame,
            fg_color=self.theme["accent"],
            corner_radius=8,
            width=50,
            height=28
        )
        version_frame.pack(side=tk.LEFT, padx=(12, 0))
        version_frame.pack_propagate(False)
        
        version = ctk.CTkLabel(
            version_frame,
            text=f"v{CURRENT_VERSION}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white"
        )
        version.pack(expand=True)
        
        self.theme_label = ctk.CTkLabel(
            logo_frame,
            text=f"• {self.theme['name']}",
            font=ctk.CTkFont(size=12),
            text_color=self.theme["accent_light"]
        )
        self.theme_label.pack(side=tk.LEFT, padx=(12, 0))
        
        # ============================================================
        # ПОИСК
        # ============================================================
        search_frame = ctk.CTkFrame(
            self.nav_panel,
            fg_color="transparent"
        )
        search_frame.place(relx=0.40, rely=0.5, anchor=tk.W, relwidth=0.35)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Поиск проектов...",
            font=ctk.CTkFont(size=13),
            height=35,
            corner_radius=10,
            fg_color=self.theme["surface"],
            text_color=self.theme["text"],
            placeholder_text_color=self.theme["text_secondary"]
        )
        self.search_entry.pack(fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # ============================================================
        # КНОПКИ
        # ============================================================
        btn_frame = ctk.CTkFrame(
            self.nav_panel,
            fg_color="transparent"
        )
        btn_frame.place(relx=0.96, rely=0.5, anchor=tk.E)
        
        # Кнопка "Добавить проект"
        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="➕",
            width=42,
            height=42,
            corner_radius=10,
            fg_color="transparent",
            hover_color=self.theme["glass"],
            text_color=self.theme["text_secondary"],
            font=ctk.CTkFont(size=20),
            command=self.add_project_dialog
        )
        self.add_btn.pack(side=tk.LEFT, padx=4)
        
        self.nav_buttons = []
        buttons = [
            ("🔄", self.check_updates_manual),
            ("🎨", self.cycle_theme),
            ("⚙", self.open_settings),
            ("✕", self.close_app)
        ]
        
        for text, cmd in buttons:
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                width=42,
                height=42,
                corner_radius=10,
                fg_color="transparent",
                hover_color=self.theme["glass"],
                text_color=self.theme["text_secondary"],
                font=ctk.CTkFont(size=18),
                command=cmd
            )
            btn.pack(side=tk.LEFT, padx=4)
            self.nav_buttons.append(btn)
            
            def on_enter(e, b=btn, t=text):
                if t == "✕":
                    b.configure(text_color="#ef4444")
                else:
                    b.configure(text_color=self.theme["accent"])
            
            def on_leave(e, b=btn):
                b.configure(text_color=self.theme["text_secondary"])
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # ============================================================
        # СТАТУС БАР
        # ============================================================
        self.status_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
            height=40,
            width=int(self.root.winfo_width() * 0.96)
        )
        self.status_frame.place(relx=0.02, rely=0.13)
        
        self.status_dot = tk.Canvas(
            self.status_frame,
            bg=self.theme["bg"],
            width=14,
            height=14,
            highlightthickness=0
        )
        self.status_dot.place(relx=0.005, rely=0.5, anchor=tk.W)
        self.dot_id = self.status_dot.create_oval(2, 2, 12, 12, fill="#10b981", outline="")
        self.dot_ring = self.status_dot.create_oval(0, 0, 14, 14, outline="#10b981", width=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="● Система активна",
            font=ctk.CTkFont(size=11),
            text_color=self.theme["text_secondary"]
        )
        self.status_label.place(relx=0.028, rely=0.5, anchor=tk.W)
        
        self.count_label = ctk.CTkLabel(
            self.status_frame,
            text="✦ 0 проектов",
            font=ctk.CTkFont(size=11),
            text_color=self.theme["text_secondary"]
        )
        self.count_label.place(relx=0.98, rely=0.5, anchor=tk.E)
        
        # ============================================================
        # КАРТОЧКИ
        # ============================================================
        self.cards_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent",
            corner_radius=0,
            width=int(self.root.winfo_width() * 0.96),
            height=int(self.root.winfo_height() * 0.80)
        )
        self.cards_frame.place(relx=0.02, rely=0.17)
    
    # ============================================================
    # ПОИСК
    # ============================================================
    
    def on_search(self, event):
        self.search_query = self.search_entry.get().strip().lower()
        self.render_projects()
    
    # ============================================================
    # ДОБАВЛЕНИЕ ПРОЕКТА
    # ============================================================
    
    def add_project_dialog(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл для добавления",
            filetypes=[
                ("Python файлы", "*.py"),
                ("Исполняемые файлы", "*.exe"),
                ("Пакетные файлы", "*.bat;*.cmd"),
                ("Ярлыки", "*.lnk;*.url"),
                ("Все файлы", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        success, message = self.project_manager.add_project(file_path)
        
        if success:
            messagebox.showinfo("✅ Успех", message)
            self.manifest = self.load_manifest()
            self.render_projects()
            self.status_label.configure(text=f"✅ {message}")
        else:
            messagebox.showerror("❌ Ошибка", message)
    
    def check_updates_manual(self):
        update_info = self.updater.check_for_updates(show_progress=True)
        if update_info:
            self.status_label.configure(text=f"🔄 Доступно обновление v{update_info['version']}")
            result = messagebox.askyesno(
                "🔄 Доступно обновление",
                f"Доступна новая версия: v{update_info['version']}\n\n"
                f"Что нового:\n{update_info['body'][:500]}{'...' if len(update_info['body']) > 500 else ''}\n\n"
                "Установить обновление?"
            )
            
            if result:
                def update_thread():
                    self.updater.download_and_update(update_info)
                
                thread = threading.Thread(target=update_thread, daemon=True)
                thread.start()
        else:
            self.status_label.configure(text="✅ У вас последняя версия")
    
    def apply_glass_effects(self):
        try:
            pywinstyles.set_opacity(self.nav_panel, color="#000001")
            pywinstyles.set_shadow(self.nav_panel, True)
        except Exception as e:
            pass
    
    def create_background(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        colors = [
            self.theme["gradient1"],
            self.theme["gradient2"],
            self.theme["gradient3"]
        ]
        
        steps = 100
        for i in range(steps):
            t = i / steps
            if t < 0.5:
                t2 = t * 2
                color = self.interpolate_color(colors[0], colors[1], t2)
            else:
                t2 = (t - 0.5) * 2
                color = self.interpolate_color(colors[1], colors[2], t2)
            
            y = i * (height / steps)
            self.bg_canvas.create_rectangle(
                0, y, width, y + height/steps + 1,
                fill=color, outline=color,
                tags="bg_gradient"
            )
    
    def interpolate_color(self, c1, c2, t):
        r1, g1, b1 = self.hex_to_rgb(c1)
        r2, g2, b2 = self.hex_to_rgb(c2)
        
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def hex_to_rgb(self, color):
        color = color.lstrip('#')
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    # ============================================================
    # ЧАСТИЦЫ
    # ============================================================
    
    def create_flow_particles(self):
        self.flow_particles = []
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        for _ in range(30):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.uniform(2, 5)
            
            img = Image.new('RGBA', (int(size*2)+4, int(size*2)+4), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            r, g, b = self.hex_to_rgb(self.theme["accent"])
            draw.ellipse((2, 2, size*2+2, size*2+2), fill=(r, g, b, 60))
            
            photo = ImageTk.PhotoImage(img)
            
            pid = self.bg_canvas.create_image(
                x, y,
                image=photo,
                tags="flow_particle"
            )
            
            self.flow_particles.append({
                "id": pid,
                "image": photo,
                "x": x,
                "y": y,
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(-0.3, 0.3),
                "size": size,
                "phase": random.uniform(0, 2 * math.pi)
            })
    
    # ============================================================
    # КАРТОЧКИ
    # ============================================================
    
    def render_projects(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        projects = self.manifest.get("projects", {})
        
        filtered_projects = {}
        if self.search_query:
            for proj_id, proj_data in projects.items():
                name = proj_data.get("name", "").lower()
                desc = proj_data.get("description", "").lower()
                tags = [tag.lower() for tag in proj_data.get("tags", [])]
                
                if (self.search_query in name or 
                    self.search_query in desc or 
                    any(self.search_query in tag for tag in tags)):
                    filtered_projects[proj_id] = proj_data
        else:
            filtered_projects = projects
        
        if not filtered_projects:
            empty_text = "📭 Нет проектов" if not self.search_query else f"🔍 Ничего не найдено по запросу '{self.search_query}'"
            empty = ctk.CTkLabel(
                self.cards_frame,
                text=empty_text,
                font=ctk.CTkFont(size=24),
                text_color=self.theme["text_secondary"]
            )
            empty.pack(expand=True)
            return
        
        self.count_label.configure(text=f"✦ {len(filtered_projects)} проектов")
        
        cards_per_row = 3
        for idx, (proj_id, proj_data) in enumerate(filtered_projects.items()):
            row = idx // cards_per_row
            col = idx % cards_per_row
            
            card_container = ctk.CTkFrame(
                self.cards_frame,
                fg_color="transparent"
            )
            card_container.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            self.cards_frame.grid_columnconfigure(col, weight=1)
            self.cards_frame.grid_rowconfigure(row, weight=1)
            
            self.create_glass_card(card_container, proj_id, proj_data)
    
    def create_glass_card(self, parent, proj_id, proj_data):
        color = proj_data.get("color", self.theme["accent"])
        proj_type = proj_data.get("type", "python")
        
        card = ctk.CTkFrame(
            parent,
            fg_color=self.theme["glass"],
            corner_radius=16,
            border_width=1,
            border_color=self.theme["glass_border"],
            width=320,
            height=350
        )
        card.pack(fill=tk.BOTH, expand=True)
        card.pack_propagate(False)
        
        top_bar = ctk.CTkFrame(
            card,
            fg_color=color,
            height=4,
            corner_radius=0
        )
        top_bar.pack(fill=tk.X, side=tk.TOP)
        
        inner = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        icon_frame = ctk.CTkFrame(
            inner,
            fg_color="transparent"
        )
        icon_frame.pack(pady=(5, 10))
        
        icon_canvas = tk.Canvas(
            icon_frame,
            bg=self.theme["glass"],
            width=70,
            height=70,
            highlightthickness=0
        )
        icon_canvas.pack()
        
        icon_canvas.create_oval(5, 5, 65, 65, fill=self.lighten_color(color, 0.3), outline="")
        icon_canvas.create_oval(10, 10, 60, 60, fill=self.lighten_color(color, 0.1), outline="")
        
        icon = ctk.CTkLabel(
            icon_canvas,
            text=proj_data.get("icon", "📦"),
            font=ctk.CTkFont(size=32),
            text_color=color
        )
        icon.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        name = ctk.CTkLabel(
            inner,
            text=proj_data.get("name", proj_id),
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.theme["text"]
        )
        name.pack()
        
        # Бейдж типа проекта
        type_colors = {
            "python": "#6c5ce7",
            "exe": "#00b894",
            "bat": "#fdcb6e",
            "cmd": "#fdcb6e",
            "url": "#0984e3",
            "lnk": "#0984e3"
        }
        type_badge = ctk.CTkLabel(
            inner,
            text=proj_type.upper(),
            font=ctk.CTkFont(size=8, weight="bold"),
            text_color=type_colors.get(proj_type, self.theme["accent_light"]),
            fg_color=self.theme["glass"],
            corner_radius=4,
            padx=6,
            pady=2
        )
        type_badge.pack(pady=(2, 0))
        
        tags = proj_data.get("tags", [])
        if tags:
            tag_frame = ctk.CTkFrame(
                inner,
                fg_color="transparent"
            )
            tag_frame.pack(pady=(6, 4))
            
            for tag in tags[:2]:
                tag_label = ctk.CTkLabel(
                    tag_frame,
                    text=f"#{tag}",
                    font=ctk.CTkFont(size=9),
                    text_color=self.theme["accent_light"],
                    fg_color=self.theme["glass"],
                    corner_radius=6,
                    padx=10,
                    pady=2
                )
                tag_label.pack(side=tk.LEFT, padx=3)
        
        desc = ctk.CTkLabel(
            inner,
            text=proj_data.get("description", ""),
            font=ctk.CTkFont(size=10),
            text_color=self.theme["text_secondary"],
            wraplength=260,
            justify="center"
        )
        desc.pack(pady=(5, 12))
        
        version = ctk.CTkLabel(
            inner,
            text=f"v{proj_data.get('version', '1.0.0')}",
            font=ctk.CTkFont(size=9),
            text_color=self.theme["text_secondary"]
        )
        version.pack(pady=(0, 10))
        
        launch_btn = ctk.CTkButton(
            inner,
            text="▶  Запустить",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=color,
            hover_color=self.darken_color(color, 0.2),
            text_color="white",
            corner_radius=8,
            width=140,
            height=36,
            command=lambda pid=proj_id: self.launch_project(pid)
        )
        launch_btn.pack()
        
        def on_enter(e):
            card.configure(fg_color=self.theme["surface_hover"])
            icon_canvas.configure(bg=self.theme["surface_hover"])
            launch_btn.configure(fg_color=self.darken_color(color, 0.2))
        
        def on_leave(e):
            card.configure(fg_color=self.theme["glass"])
            icon_canvas.configure(bg=self.theme["glass"])
            launch_btn.configure(fg_color=color)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        return card
    
    def lighten_color(self, color, factor):
        r, g, b = self.hex_to_rgb(color)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def darken_color(self, color, factor):
        r, g, b = self.hex_to_rgb(color)
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    # ============================================================
    # ЗАПУСК ПРОЕКТОВ
    # ============================================================
    
    def launch_project(self, project_id):
        proj_data = self.manifest["projects"].get(project_id)
        if not proj_data:
            messagebox.showerror("Ошибка", f"Проект {project_id} не найден!")
            return
        
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = self.base_dir
        
        proj_path = os.path.join(base, proj_data.get("path", ""))
        
        if not os.path.exists(proj_path):
            messagebox.showerror("Ошибка", f"Файл не найден:\n{proj_path}")
            return
        
        try:
            self.status_label.configure(text=f"🚀 Запуск {proj_data['name']}...")
            
            proj_type = proj_data.get("type", "python")
            
            if getattr(sys, 'frozen', False):
                if proj_type == "exe":
                    subprocess.Popen([proj_path], shell=True)
                elif proj_type in ["bat", "cmd"]:
                    subprocess.Popen([proj_path], shell=True)
                elif proj_type == "url":
                    subprocess.Popen(['start', proj_path], shell=True)
                elif proj_type == "lnk":
                    subprocess.Popen([proj_path], shell=True)
                else:
                    cmd = f'start cmd /k "py "{proj_path}""'
                    subprocess.Popen(cmd, shell=True)
            else:
                subprocess.Popen([sys.executable, proj_path], shell=True)
            
            self.status_label.configure(text=f"● {proj_data['name']} запущен")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить {proj_data['name']}:\n{str(e)}")
            self.status_label.configure(text=f"✕ Ошибка запуска {proj_data['name']}")
    
    # ============================================================
    # АНИМАЦИЯ
    # ============================================================
    
    def animate(self):
        self.anim_time += 0.02
        
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        for p in self.flow_particles:
            p["x"] += p["vx"] + math.sin(self.anim_time + p["phase"]) * 0.1
            p["y"] += p["vy"] + math.cos(self.anim_time * 0.7 + p["phase"]) * 0.1
            
            if p["x"] < 0 or p["x"] > width:
                p["vx"] *= -1
            if p["y"] < 0 or p["y"] > height:
                p["vy"] *= -1
            
            self.bg_canvas.coords(p["id"], p["x"], p["y"])
        
        dot_size = 4 + 3 * (0.5 + 0.5 * math.sin(self.anim_time * 3))
        self.status_dot.coords(
            self.dot_id,
            7 - dot_size/2, 7 - dot_size/2,
            7 + dot_size/2, 7 + dot_size/2
        )
        
        ring_size = 6 + 3 * (0.5 + 0.5 * math.sin(self.anim_time * 2))
        self.status_dot.coords(
            self.dot_ring,
            7 - ring_size, 7 - ring_size,
            7 + ring_size, 7 + ring_size
        )
        
        colors = [self.theme["accent"], "#10b981", self.theme["accent_light"]]
        idx = int((self.anim_time * 0.4) % len(colors))
        self.status_dot.itemconfig(self.dot_id, fill=colors[idx])
        self.status_dot.itemconfig(self.dot_ring, outline=colors[idx])
        
        self.root.after(50, self.animate)
    
    # ============================================================
    # СТАРТОВАЯ АНИМАЦИЯ
    # ============================================================
    
    def fade_in(self):
        self.root.attributes('-alpha', 0.0)
        
        def fade():
            alpha = self.root.attributes('-alpha')
            if alpha < 1.0:
                alpha += 0.03
                self.root.attributes('-alpha', alpha)
                self.root.after(16, fade)
        
        fade()
    
    # ============================================================
    # ПЕРЕКЛЮЧЕНИЕ ТЕМ
    # ============================================================
    
    def cycle_theme(self):
        themes = list(self.themes.keys())
        current_idx = themes.index(self.current_theme)
        next_idx = (current_idx + 1) % len(themes)
        self.apply_theme(themes[next_idx])
    
    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        self.theme = self.themes[theme_name]
        
        self.settings["theme"] = theme_name
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)
        
        self.refresh_ui()
        self.status_label.configure(text=f"✨ Тема: {self.theme['name']}")
    
    def refresh_ui(self):
        self.root.configure(bg=self.theme["bg"])
        self.main_frame.configure(fg_color=self.theme["bg"])
        self.bg_canvas.configure(bg=self.theme["bg"])
        
        self.bg_canvas.delete("all")
        self.create_background()
        
        self.bg_canvas.delete("flow_particle")
        self.create_flow_particles()
        
        self.nav_panel.configure(fg_color=self.theme["glass"])
        self.logo.configure(text_color=self.theme["text"])
        self.theme_label.configure(text=f"• {self.theme['name']}", text_color=self.theme["accent_light"])
        
        self.search_entry.configure(
            fg_color=self.theme["surface"],
            text_color=self.theme["text"],
            placeholder_text_color=self.theme["text_secondary"]
        )
        
        for btn in self.nav_buttons:
            btn.configure(text_color=self.theme["text_secondary"])
        
        self.status_dot.configure(bg=self.theme["bg"])
        self.status_label.configure(text_color=self.theme["text_secondary"])
        self.count_label.configure(text_color=self.theme["text_secondary"])
        
        self.render_projects()
    
    # ============================================================
    # НАСТРОЙКИ
    # ============================================================
    
    def open_settings(self):
        settings = ctk.CTkToplevel(self.root)
        settings.title("✦ Настройки ✦")
        settings.geometry("550x550")
        settings.configure(fg_color=self.theme["bg"])
        settings.transient(self.root)
        settings.grab_set()
        
        ctk.CTkLabel(
            settings,
            text="✦ Настройки",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.theme["text"]
        ).pack(pady=(20, 10))
        
        container = ctk.CTkScrollableFrame(
            settings,
            fg_color="transparent",
            corner_radius=0
        )
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # --- Раздел: Тема ---
        ctk.CTkLabel(
            container,
            text="🎨 Выберите тему:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme["text"]
        ).pack(anchor=tk.W, pady=(0, 15))
        
        theme_grid = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )
        theme_grid.pack(fill=tk.X)
        
        row = 0
        col = 0
        for theme_name, theme_data in self.themes.items():
            is_active = theme_name == self.current_theme
            
            theme_btn = ctk.CTkButton(
                theme_grid,
                text=theme_data["name"],
                width=100,
                height=50,
                corner_radius=10,
                fg_color=self.theme["accent"] if is_active else self.theme["glass"],
                hover_color=self.theme["accent_hover"],
                text_color="white" if is_active else self.theme["text_secondary"],
                font=ctk.CTkFont(size=12, weight="bold" if is_active else "normal"),
                border_width=2 if is_active else 1,
                border_color=self.theme["accent"] if is_active else self.theme["glass_border"],
                command=lambda t=theme_name: [self.apply_theme(t), settings.destroy()]
            )
            theme_btn.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        # Разделитель
        ctk.CTkFrame(
            container,
            fg_color=self.theme["glass_border"],
            height=1
        ).pack(fill=tk.X, pady=20)
        
        # --- Раздел: Обновления ---
        ctk.CTkLabel(
            container,
            text="🔄 Обновления:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme["text"]
        ).pack(anchor=tk.W, pady=(0, 10))
        
        ctk.CTkButton(
            container,
            text="🔍 Проверить обновления сейчас",
            width=200,
            height=40,
            corner_radius=10,
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent_hover"],
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.check_updates_manual
        ).pack(anchor=tk.W, pady=(0, 5))
        
        version_info = ctk.CTkLabel(
            container,
            text=f"Текущая версия: v{CURRENT_VERSION}",
            font=ctk.CTkFont(size=11),
            text_color=self.theme["text_secondary"]
        )
        version_info.pack(anchor=tk.W, pady=(0, 20))
        
        # Разделитель
        ctk.CTkFrame(
            container,
            fg_color=self.theme["glass_border"],
            height=1
        ).pack(fill=tk.X, pady=10)
        
        ctk.CTkButton(
            container,
            text="Закрыть",
            width=150,
            height=45,
            corner_radius=10,
            fg_color=self.theme["glass"],
            hover_color=self.theme["glass_border"],
            text_color=self.theme["text_secondary"],
            font=ctk.CTkFont(size=12),
            command=settings.destroy
        ).pack(pady=20)
    
    # ============================================================
    # УПРАВЛЕНИЕ ОКНОМ
    # ============================================================
    
    def make_draggable(self):
        def start_move(e):
            self._drag_x = e.x
            self._drag_y = e.y
        
        def on_move(e):
            x = self.root.winfo_x() + e.x - self._drag_x
            y = self.root.winfo_y() + e.y - self._drag_y
            self.root.geometry(f"+{x}+{y}")
        
        self.nav_panel.bind("<Button-1>", start_move)
        self.nav_panel.bind("<B1-Motion>", on_move)
    
    def close_app(self):
        if messagebox.askyesno("Выход", "Закрыть NeoLauncher?"):
            self.root.quit()
            self.root.destroy()


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    root = ctk.CTk()
    app = NeoLauncher(root)
    root.mainloop()