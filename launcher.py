import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import subprocess
import threading
import math
import random
from datetime import datetime

# ============================================================
# ЯЗЫКИ
# ============================================================

LANGUAGES = {
    "ru": {
        "name": "Русский",
        "app_title": "✦ NeoBrain Launcher ✦",
        "app_subtitle": "Лаунчер проектов NeoBrain",
        "status_active": "✦ СИСТЕМА АКТИВНА",
        "status_projects": "✦ ПРОЕКТОВ ГОТОВЫ К ЗАПУСКУ",
        "status_ready": "✦ {count} ПРОЕКТОВ ГОТОВЫ К ЗАПУСКУ",
        "status_launch": "🚀 ЗАПУСК {name}...",
        "status_launched": "✦ {name} ЗАПУЩЕН",
        "status_error": "❌ ОШИБКА ЗАПУСКА {name}",
        "status_saved": "✅ НАСТРОЙКИ СОХРАНЕНЫ!",
        "status_no_projects": "❌ Нет проектов в манифесте!",
        "status_file_not_found": "✧ ФАЙЛ НЕ НАЙДЕН",
        "status_file_ready": "✦ ГОТОВ К ЗАПУСКУ",
        "status_loading": "📂 Загрузка манифеста...",
        "btn_launch": "▶ ЗАПУСТИТЬ",
        "btn_settings": "✦",
        "btn_save": "💾 СОХРАНИТЬ",
        "btn_reset_camera": "Сброс камеры (Ctrl+0)",
        "btn_clear": "Удалить выделенное (Del)",
        "btn_select_all": "Выделить всё (Ctrl+A)",
        "btn_special": "🧠 Странный режим (Пробел)",
        "btn_emergency": "⚠️ АВАРИЙНЫЙ СБРОС (X)",
        "settings_title": "✦ НАСТРОЙКИ",
        "settings_auto_update": "Автоматически проверять обновления",
        "settings_language": "🌐 Язык / Language:",
        "footer": "✦ ВСЕ ПРОЕКТЫ В ОДНОЙ ПАПКЕ — ОБНОВЛЯЙ ПЕРЕТАСКИВАНИЕМ ✦",
        "select_lang_title": "🌐 Выбор языка",
        "select_lang_question": "Выберите язык / Select language:",
        "select_lang_remember": "Запомнить выбор (больше не спрашивать)",
        "select_lang_btn_ok": "✅ Применить",
        "version": "v3.0",
        "no_projects": "Нет проектов",
        "project_type_python": "python",
        "project_type_exe": "exe",
        "project_launches": "запусков",
        "file_not_found_error": "Файл не найден:\n{path}",
        "project_not_found_error": "Проект {id} не найден!",
        "launch_error": "Не удалось запустить {name}:\n{error}",
        "settings_saved": "✅ НАСТРОЙКИ СОХРАНЕНЫ!",
        "save_error": "Не удалось сохранить настройки",
        "lang_changed": "🌐 Язык изменён. Перезапустите лаунчер.",
        "lang_changed_title": "Язык изменён",
        "lang_restart": "Для применения языка перезапустите лаунчер.",
        "emergency_reset": "💥 АВАРИЙНЫЙ СБРОС ВЫПОЛНЕН!"
    },
    "en": {
        "name": "English",
        "app_title": "✦ NeoBrain Launcher ✦",
        "app_subtitle": "NeoBrain Projects Launcher",
        "status_active": "✦ SYSTEM ACTIVE",
        "status_projects": "✦ PROJECTS READY TO LAUNCH",
        "status_ready": "✦ {count} PROJECTS READY TO LAUNCH",
        "status_launch": "🚀 LAUNCHING {name}...",
        "status_launched": "✦ {name} LAUNCHED",
        "status_error": "❌ LAUNCH ERROR {name}",
        "status_saved": "✅ SETTINGS SAVED!",
        "status_no_projects": "❌ No projects in manifest!",
        "status_file_not_found": "✧ FILE NOT FOUND",
        "status_file_ready": "✦ READY TO LAUNCH",
        "status_loading": "📂 Loading manifest...",
        "btn_launch": "▶ LAUNCH",
        "btn_settings": "✦",
        "btn_save": "💾 SAVE",
        "btn_reset_camera": "Reset Camera (Ctrl+0)",
        "btn_clear": "Delete Selected (Del)",
        "btn_select_all": "Select All (Ctrl+A)",
        "btn_special": "🧠 Strange Mode (Space)",
        "btn_emergency": "⚠️ EMERGENCY RESET (X)",
        "settings_title": "✦ SETTINGS",
        "settings_auto_update": "Check for updates automatically",
        "settings_language": "🌐 Language / Язык:",
        "footer": "✦ ALL PROJECTS IN ONE FOLDER — UPDATE BY DRAGGING ✦",
        "select_lang_title": "🌐 Language Selection",
        "select_lang_question": "Select language / Выберите язык:",
        "select_lang_remember": "Remember my choice (don't ask again)",
        "select_lang_btn_ok": "✅ Apply",
        "version": "v3.0",
        "no_projects": "No projects",
        "project_type_python": "python",
        "project_type_exe": "exe",
        "project_launches": "launches",
        "file_not_found_error": "File not found:\n{path}",
        "project_not_found_error": "Project {id} not found!",
        "launch_error": "Failed to launch {name}:\n{error}",
        "settings_saved": "✅ SETTINGS SAVED!",
        "save_error": "Failed to save settings",
        "lang_changed": "🌐 Language changed. Please restart launcher.",
        "lang_changed_title": "Language Changed",
        "lang_restart": "Please restart launcher to apply language changes.",
        "emergency_reset": "💥 EMERGENCY RESET COMPLETED!"
    }
}

# ============================================================
# КЛАСС ЛАУНЧЕРА
# ============================================================

class NeoBrainLauncher:
    def __init__(self, root):
        self.root = root
        self.lang = self.load_language()
        self.T = LANGUAGES.get(self.lang, LANGUAGES["ru"])
        
        self.root.title(self.T["app_title"])
        self.root.geometry("1200x750")
        self.root.minsize(1000, 600)
        self.root.configure(bg="#050510")
        self.root.resizable(True, True)
        
        # Цветовая схема
        self.bg_dark = "#050510"
        self.bg_medium = "#0a0a20"
        self.bg_light = "#151530"
        self.card_bg = "#0f0f2a"
        self.card_hover = "#1a1a4a"
        
        self.text_primary = "#f0e8ff"
        self.text_secondary = "#8a7aaa"
        self.text_accent = "#ff2d8a"
        
        self.colors = {
            "pink": "#ff2d8a",
            "hot_pink": "#ff1493",
            "purple": "#a855f7",
            "deep_purple": "#7c3aed",
            "red": "#ff0040",
            "blue": "#3b82f6",
            "cyan": "#06b6d4",
            "gold": "#fbbf24",
            "green": "#10b981",
            "white": "#ffffff"
        }
        
        self.animation_angle = 0
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"📁 Базовая папка: {self.base_dir}")
        
        self.manifest_path = os.path.join(self.base_dir, "manifest.json")
        self.settings_path = os.path.join(self.base_dir, "launcher_settings.json")
        
        self.manifest = self.load_manifest()
        self.settings = self.load_settings()
        
        self.setup_ui()
        self.render_projects()
        self.animate()
    
    # ============================================================
    # ЯЗЫК
    # ============================================================
    
    def load_language(self):
        """Загружает язык из настроек или показывает окно выбора"""
        settings = self.load_settings()
        lang = settings.get("language", None)
        
        if lang and lang in LANGUAGES:
            return lang
        
        # Первый запуск — показываем выбор языка
        return self.show_language_selector()
    
    def show_language_selector(self):
        """Окно выбора языка при первом запуске"""
        selector = tk.Toplevel(self.root)
        selector.title("🌐 Language / Язык")
        selector.geometry("450x320")
        selector.configure(bg="#0a0a20")
        selector.resizable(False, False)
        selector.transient(self.root)
        selector.grab_set()
        
        # Центрируем
        selector.update_idletasks()
        x = (self.root.winfo_screenwidth() - 450) // 2
        y = (self.root.winfo_screenheight() - 320) // 2
        selector.geometry(f"+{x}+{y}")
        
        # Заголовок
        tk.Label(
            selector,
            text="🌐 Language / Язык",
            font=("Segoe UI", 18, "bold"),
            bg="#0a0a20",
            fg="#f0e8ff"
        ).pack(pady=20)
        
        tk.Label(
            selector,
            text="Select language / Выберите язык:",
            font=("Segoe UI", 12),
            bg="#0a0a20",
            fg="#8a7aaa"
        ).pack(pady=(0, 15))
        
        # Выбор языка
        lang_var = tk.StringVar(value="ru")
        
        lang_frame = tk.Frame(selector, bg="#0a0a20")
        lang_frame.pack(pady=5)
        
        tk.Radiobutton(
            lang_frame,
            text="🇷🇺 Русский",
            variable=lang_var,
            value="ru",
            bg="#0a0a20",
            fg="#f0e8ff",
            selectcolor="#0a0a20",
            font=("Segoe UI", 13)
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Radiobutton(
            lang_frame,
            text="🇬🇧 English",
            variable=lang_var,
            value="en",
            bg="#0a0a20",
            fg="#f0e8ff",
            selectcolor="#0a0a20",
            font=("Segoe UI", 13)
        ).pack(side=tk.LEFT, padx=20)
        
        # Галочка "запомнить"
        remember_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            selector,
            text="Запомнить выбор (больше не спрашивать) / Remember my choice",
            variable=remember_var,
            bg="#0a0a20",
            fg="#8a7aaa",
            selectcolor="#0a0a20",
            font=("Segoe UI", 10)
        ).pack(pady=15)
        
        # Кнопка
        def apply_language():
            lang = lang_var.get()
            if remember_var.get():
                settings = self.load_settings()
                settings["language"] = lang
                self.save_settings(settings)
            selector.destroy()
            self.lang = lang
            self.T = LANGUAGES.get(lang, LANGUAGES["ru"])
            self.root.title(self.T["app_title"])
            # Обновляем UI
            self.setup_ui()
            self.render_projects()
        
        tk.Button(
            selector,
            text="✅ Применить / Apply",
            font=("Segoe UI", 12, "bold"),
            bg="#ff2d8a",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=apply_language,
            cursor="hand2"
        ).pack(pady=15)
        
        # Ждём выбора
        self.root.wait_window(selector)
        return self.lang
    
    # ============================================================
    # НАСТРОЙКИ
    # ============================================================
    
    def load_settings(self):
        default_settings = {
            "auto_update": True,
            "language": None  # None = первый запуск
        }
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Обновляем дефолтные настройки
                    for key in default_settings:
                        if key not in data:
                            data[key] = default_settings[key]
                    return data
            else:
                with open(self.settings_path, 'w', encoding='utf-8') as f:
                    json.dump(default_settings, f, indent=2, ensure_ascii=False)
                return default_settings
        except:
            return default_settings
    
    def save_settings(self, settings):
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    # ============================================================
    # МАНИФЕСТ
    # ============================================================
    
    def load_manifest(self):
        try:
            if os.path.exists(self.manifest_path):
                with open(self.manifest_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ Манифест загружен: {len(data.get('projects', {}))} проектов")
                    return data
            else:
                print("❌ Файл manifest.json не найден!")
                default = {
                    "projects": {
                        "neobrain": {
                            "name": "NeoBrain",
                            "version": "3.5.0",
                            "path": "projects/neobrain.py",
                            "icon": "🧠",
                            "color": "#ff2d8a",
                            "description": "Локальный AI-чат с персонажами",
                            "tags": ["AI", "Chat"],
                            "type": "python"
                        },
                        "neospace": {
                            "name": "NeoSpace-Pro",
                            "version": "1.0.0",
                            "path": "projects/neospace.py",
                            "icon": "🖥️",
                            "color": "#8b5cf6",
                            "description": "Виртуальная среда для экспериментов",
                            "tags": ["Virtual", "Sandbox"],
                            "type": "python"
                        },
                        "whydoes": {
                            "name": "Why-Does-This-Exist",
                            "version": "1.0.0",
                            "path": "projects/whydoes.py",
                            "icon": "🌀",
                            "color": "#fbbf24",
                            "description": "Генератор визуального безумия",
                            "tags": ["Visual", "Art"],
                            "type": "python"
                        }
                    }
                }
                with open(self.manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(default, f, indent=2, ensure_ascii=False)
                return default
        except Exception as e:
            print(f"❌ Ошибка загрузки манифеста: {e}")
            return {"projects": {}}
    
    # ============================================================
    # UI
    # ============================================================
    
    def setup_ui(self):
        # Очищаем старый UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.main_frame = tk.Frame(self.root, bg=self.bg_dark)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        self.bg_canvas = tk.Canvas(
            self.main_frame,
            bg=self.bg_dark,
            highlightthickness=0
        )
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.create_deep_gradient_bg()
        
        header_frame = tk.Frame(self.main_frame, bg=self.bg_dark)
        header_frame.place(relx=0, rely=0, relwidth=1, height=100)
        
        title = tk.Label(
            header_frame,
            text=self.T["app_title"].replace(" ✦", ""),
            font=("Segoe UI", 34, "bold"),
            bg=self.bg_dark,
            fg=self.text_primary
        )
        title.place(relx=0.03, rely=0.5, anchor=tk.W)
        
        version_label = tk.Label(
            header_frame,
            text=self.T["version"],
            font=("Segoe UI", 13, "bold"),
            bg=self.bg_dark,
            fg=self.text_secondary
        )
        version_label.place(relx=0.2, rely=0.5, anchor=tk.W)
        
        # Кнопка настроек с языком
        settings_btn = tk.Button(
            header_frame,
            text="⚙️",
            font=("Segoe UI", 18),
            bg=self.bg_dark,
            fg="#ff2d8a",
            relief=tk.FLAT,
            command=self.open_settings,
            cursor="hand2"
        )
        settings_btn.place(relx=0.98, rely=0.5, anchor=tk.E)
        
        status_frame = tk.Frame(self.main_frame, bg=self.bg_dark)
        status_frame.place(relx=0, rely=0.15, relwidth=1, height=45)
        
        self.status_dot = tk.Canvas(
            status_frame,
            bg=self.bg_dark,
            width=14,
            height=14,
            highlightthickness=0
        )
        self.status_dot.place(relx=0.03, rely=0.5, anchor=tk.W)
        self.status_dot_id = self.status_dot.create_oval(2, 2, 12, 12, fill="#ff2d8a", outline="")
        
        self.status_label = tk.Label(
            status_frame,
            text=self.T["status_active"],
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_dark,
            fg=self.text_secondary
        )
        self.status_label.place(relx=0.055, rely=0.5, anchor=tk.W)
        
        self.cards_frame = tk.Frame(self.main_frame, bg=self.bg_dark)
        self.cards_frame.place(relx=0, rely=0.23, relwidth=1, relheight=0.7)
        
        footer = tk.Frame(self.main_frame, bg=self.bg_dark)
        footer.place(relx=0, rely=0.95, relwidth=1, height=35)
        
        footer_text = tk.Label(
            footer,
            text=self.T["footer"],
            font=("Segoe UI", 9),
            bg=self.bg_dark,
            fg="#2a2a5a"
        )
        footer_text.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def create_deep_gradient_bg(self):
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        
        colors = [(5, 5, 16), (10, 5, 20), (15, 10, 30), (5, 5, 16)]
        steps = 100
        
        for i in range(steps):
            t = i / steps
            idx = t * (len(colors) - 1)
            idx1 = int(idx)
            idx2 = min(idx1 + 1, len(colors) - 1)
            frac = idx - idx1
            
            r1, g1, b1 = colors[idx1]
            r2, g2, b2 = colors[idx2]
            
            r = int(r1 + (r2 - r1) * frac)
            g = int(g1 + (g2 - g1) * frac)
            b = int(b1 + (b2 - b1) * frac)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            y = i * (height / steps)
            self.bg_canvas.create_rectangle(
                0, y, width, y + height/steps + 1,
                fill=color, outline=color
            )
        
        self.neon_particles = []
        for _ in range(25):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 5)
            colors_list = ["#ff2d8a", "#ff1493", "#a855f7", "#7c3aed", "#fbbf24"]
            color = random.choice(colors_list)
            
            particle_id = self.bg_canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=color, outline="",
                tags="neon_particle"
            )
            
            self.neon_particles.append({
                "id": particle_id,
                "x": x, "y": y,
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(-0.3, 0.3),
                "size": size,
                "color": color
            })
    
    def render_projects(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        projects = self.manifest.get("projects", {})
        print(f"Найдено проектов: {len(projects)}")
        
        if not projects:
            self.status_label.config(text=self.T["status_no_projects"])
            return
        
        row_frame = tk.Frame(self.cards_frame, bg=self.bg_dark)
        row_frame.pack(fill=tk.BOTH, expand=True)
        
        for idx, (project_id, project_data) in enumerate(projects.items()):
            self.create_project_card(row_frame, project_id, project_data, idx)
        
        self.status_label.config(text=self.T["status_ready"].format(count=len(projects)))
    
    def create_project_card(self, parent, project_id, project_data, idx):
        glow_color = project_data.get("color", "#ff2d8a")
        name = project_data.get("name", project_id)
        icon = project_data.get("icon", "📦")
        description = project_data.get("description", "")
        
        card = tk.Frame(
            parent,
            bg=self.card_bg,
            relief=tk.FLAT,
            bd=2,
            highlightbackground=glow_color,
            highlightthickness=2,
            width=300,
            height=350
        )
        card.grid(row=0, column=idx, sticky="nsew", padx=15, pady=10)
        parent.grid_columnconfigure(idx, weight=1)
        card.pack_propagate(False)
        
        inner = tk.Frame(card, bg=self.card_bg)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        icon_label = tk.Label(
            inner,
            text=icon,
            font=("Segoe UI", 36),
            bg=self.card_bg,
            fg=glow_color
        )
        icon_label.pack(pady=(0, 10))
        
        name_label = tk.Label(
            inner,
            text=name,
            font=("Segoe UI", 18, "bold"),
            bg=self.card_bg,
            fg=self.text_primary
        )
        name_label.pack()
        
        tags = project_data.get("tags", [])
        if tags:
            tag_text = "  ".join([f"#{tag}" for tag in tags])
            tag_label = tk.Label(
                inner,
                text=tag_text,
                font=("Segoe UI", 9),
                bg=self.card_bg,
                fg=self.text_secondary
            )
            tag_label.pack(pady=(5, 5))
        
        desc_label = tk.Label(
            inner,
            text=description,
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg=self.text_secondary,
            wraplength=240,
            justify=tk.CENTER
        )
        desc_label.pack(pady=(0, 10))
        
        status = self.get_project_status(project_id, project_data)
        status_label = tk.Label(
            inner,
            text=status["text"],
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg=status["color"]
        )
        status_label.pack()
        
        version = project_data.get("version", "?")
        version_label = tk.Label(
            inner,
            text=f"v{version}",
            font=("Segoe UI", 9),
            bg=self.card_bg,
            fg="#3a3a6a"
        )
        version_label.pack(pady=(2, 8))
        
        launch_btn = tk.Button(
            inner,
            text=self.T["btn_launch"],
            font=("Segoe UI", 11, "bold"),
            bg=glow_color,
            fg="#ffffff",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=lambda pid=project_id: self.launch_project(pid),
            cursor="hand2"
        )
        launch_btn.pack()
        
        def on_enter(e):
            card.config(highlightbackground="#ffffff", highlightthickness=3)
            inner.config(bg=self.card_hover)
            for child in inner.winfo_children():
                if isinstance(child, tk.Frame):
                    child.config(bg=self.card_hover)
                elif isinstance(child, tk.Label) and child.cget("bg") != self.bg_dark:
                    child.config(bg=self.card_hover)
        
        def on_leave(e):
            card.config(highlightbackground=glow_color, highlightthickness=2)
            inner.config(bg=self.card_bg)
            for child in inner.winfo_children():
                if isinstance(child, tk.Frame):
                    child.config(bg=self.card_bg)
                elif isinstance(child, tk.Label) and child.cget("bg") != self.bg_dark:
                    child.config(bg=self.card_bg)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
    
    def get_project_status(self, project_id, project_data):
        project_path = os.path.join(self.base_dir, project_data.get("path", ""))
        print(f"🔍 Проверка пути для {project_id}: {project_path}")
        print(f"📁 Файл существует: {os.path.exists(project_path)}")
        
        if os.path.exists(project_path):
            return {"text": self.T["status_file_ready"], "color": "#10b981"}
        else:
            return {"text": self.T["status_file_not_found"], "color": "#ff2d8a"}
    
    def animate(self):
        self.animation_angle += 0.03
        
        dot_size = 4 + 3 * (0.5 + 0.5 * math.sin(self.animation_angle * 3))
        self.status_dot.coords(self.status_dot_id, 7 - dot_size/2, 7 - dot_size/2, 7 + dot_size/2, 7 + dot_size/2)
        
        neon_colors = ["#ff2d8a", "#ff1493", "#a855f7", "#7c3aed", "#fbbf24", "#ff2d8a"]
        idx = int((self.animation_angle * 0.4) % len(neon_colors))
        self.status_dot.itemconfig(self.status_dot_id, fill=neon_colors[idx])
        
        for particle in self.neon_particles:
            x = particle["x"] + particle["vx"]
            y = particle["y"] + particle["vy"]
            if x < 0 or x > self.root.winfo_screenwidth(): particle["vx"] *= -1
            if y < 0 or y > self.root.winfo_screenheight(): particle["vy"] *= -1
            particle["x"] = x
            particle["y"] = y
            size = particle["size"] * (0.6 + 0.4 * math.sin(self.animation_angle * 2 + particle["x"]))
            self.bg_canvas.coords(particle["id"], x - size, y - size, x + size, y + size)
        
        self.root.after(50, self.animate)
    
    # ============================================================
    # ЗАПУСК ПРОЕКТОВ
    # ============================================================
    
    def launch_project(self, project_id):
        project_data = self.manifest["projects"].get(project_id)
        if not project_data:
            messagebox.showerror("Error", self.T["project_not_found_error"].format(id=project_id))
            return
        
        project_path = os.path.join(self.base_dir, project_data.get("path", ""))
        print(f"🚀 Запуск {project_id}: {project_path}")
        
        if not os.path.exists(project_path):
            messagebox.showerror("Error", self.T["file_not_found_error"].format(path=project_path))
            return
        
        try:
            self.status_label.config(text=self.T["status_launch"].format(name=project_data["name"]))
            if project_data.get("type") == "python":
                subprocess.Popen([sys.executable, project_path], shell=True)
            else:
                subprocess.Popen([project_path], shell=True)
            self.status_label.config(text=self.T["status_launched"].format(name=project_data["name"]))
        except Exception as e:
            messagebox.showerror("Error", self.T["launch_error"].format(name=project_data["name"], error=str(e)))
            self.status_label.config(text=self.T["status_error"].format(name=project_data["name"]))
    
    # ============================================================
    # НАСТРОЙКИ
    # ============================================================
    
    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title(self.T["settings_title"])
        settings_window.geometry("450x420")
        settings_window.configure(bg=self.bg_medium)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        title = tk.Label(
            settings_window,
            text=self.T["settings_title"],
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_medium,
            fg=self.text_primary
        )
        title.pack(pady=25)
        
        frame = tk.Frame(settings_window, bg=self.bg_medium)
        frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Автообновление
        auto_var = tk.BooleanVar(value=self.settings.get("auto_update", True))
        auto_check = tk.Checkbutton(
            frame,
            text=self.T["settings_auto_update"],
            variable=auto_var,
            bg=self.bg_medium,
            fg=self.text_secondary,
            selectcolor=self.bg_medium,
            font=("Segoe UI", 11)
        )
        auto_check.pack(anchor=tk.W, pady=8)
        
        separator = tk.Frame(frame, bg="#2a2a5a", height=1)
        separator.pack(fill=tk.X, pady=10)
        
        # Выбор языка
        tk.Label(
            frame,
            text=self.T["settings_language"],
            bg=self.bg_medium,
            fg=self.text_secondary,
            font=("Segoe UI", 11)
        ).pack(anchor=tk.W, pady=5)
        
        lang_var = tk.StringVar(value=self.lang)
        
        lang_frame = tk.Frame(frame, bg=self.bg_medium)
        lang_frame.pack(anchor=tk.W, pady=5)
        
        tk.Radiobutton(
            lang_frame,
            text="🇷🇺 Русский",
            variable=lang_var,
            value="ru",
            bg=self.bg_medium,
            fg=self.text_secondary,
            selectcolor=self.bg_medium,
            font=("Segoe UI", 11)
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Radiobutton(
            lang_frame,
            text="🇬🇧 English",
            variable=lang_var,
            value="en",
            bg=self.bg_medium,
            fg=self.text_secondary,
            selectcolor=self.bg_medium,
            font=("Segoe UI", 11)
        ).pack(side=tk.LEFT, padx=10)
        
        separator2 = tk.Frame(frame, bg="#2a2a5a", height=1)
        separator2.pack(fill=tk.X, pady=10)
        
        def save():
            self.settings["auto_update"] = auto_var.get()
            if lang_var.get() != self.lang:
                # Язык изменился
                old_lang = self.lang
                self.lang = lang_var.get()
                self.T = LANGUAGES.get(self.lang, LANGUAGES["ru"])
                self.settings["language"] = self.lang
                
                # Сохраняем настройки
                self.save_settings(self.settings)
                
                # Показываем сообщение о смене языка
                messagebox.showinfo(
                    self.T["lang_changed_title"],
                    self.T["lang_restart"]
                )
            else:
                self.save_settings(self.settings)
                self.status_label.config(text=self.T["status_saved"])
            
            settings_window.destroy()
            # Перезапускаем UI для обновления текстов
            self.setup_ui()
            self.render_projects()
        
        save_btn = tk.Button(
            settings_window,
            text=self.T["btn_save"],
            font=("Segoe UI", 12, "bold"),
            bg="#ff2d8a",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=save,
            cursor="hand2"
        )
        save_btn.pack(pady=25)


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = NeoBrainLauncher(root)
    root.mainloop()