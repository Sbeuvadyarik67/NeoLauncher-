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

class NeoBrainLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("✦ NeoBrain Launcher ✦")
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
        
        # Неоновые цвета
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
        self.manifest_path = os.path.join(self.base_dir, "manifest.json")
        self.settings_path = os.path.join(self.base_dir, "launcher_settings.json")
        
        self.manifest = self.load_manifest()
        self.settings = self.load_settings()
        
        self.setup_ui()
        self.render_projects()
        self.animate()
    
    def load_manifest(self):
        default_manifest = {
            "projects": {
                "neobrain": {
                    "name": "NeoBrain",
                    "version": "2.1.2",
                    "path": "C:/Users/Вадим/Desktop/Общее/Вадим разработка/_РАБОЧАЯ ВЕРСИЯ_/github/NeoBrain/main.py",
                    "icon": "🧠",
                    "color": "#ff2d8a",
                    "description": "Локальный AI-чат с персонажами",
                    "tags": ["AI", "Chat"],
                    "type": "python"
                },
                "neospace": {
                    "name": "NeoSpace-Pro",
                    "version": "1.0.0",
                    "path": "C:/Users/Вадим/Desktop/Общее/Вадим разработка/_РАБОЧАЯ ВЕРСИЯ_/github/NeoSpace/virtual_minimal.py",
                    "icon": "🖥️",
                    "color": "#8b5cf6",
                    "description": "Виртуальная среда для экспериментов",
                    "tags": ["Virtual", "Sandbox"],
                    "type": "python"
                },
                "whydoes": {
                    "name": "Why-Does-This-Exist",
                    "version": "1.0.0",
                    "path": "C:/Users/Вадим/NeoLauncher-/projects/whydoes/abstract_madness.py",
                    "icon": "🌀",
                    "color": "#fbbf24",
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
                    json.dump(default_manifest, f, indent=2, ensure_ascii=False)
                return default_manifest
        except Exception as e:
            print(f"Ошибка загрузки манифеста: {e}")
            return default_manifest
    
    def load_settings(self):
        default_settings = {"auto_update": True}
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(self.settings_path, 'w', encoding='utf-8') as f:
                    json.dump(default_settings, f, indent=2, ensure_ascii=False)
                return default_settings
        except:
            return default_settings
    
    def setup_ui(self):
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
            text="✦ NeoBrain",
            font=("Segoe UI", 34, "bold"),
            bg=self.bg_dark,
            fg=self.text_primary
        )
        title.place(relx=0.03, rely=0.5, anchor=tk.W)
        
        version_label = tk.Label(
            header_frame,
            text="v2.0",
            font=("Segoe UI", 13, "bold"),
            bg=self.bg_dark,
            fg=self.text_secondary
        )
        version_label.place(relx=0.2, rely=0.5, anchor=tk.W)
        
        settings_btn = tk.Button(
            header_frame,
            text="✦",
            font=("Segoe UI", 20),
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
            text="✦ СИСТЕМА АКТИВНА",
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
            text="✦ ВСЕ ПРОЕКТЫ РАСПРОСТРАНЯЮТСЯ БЕСПЛАТНО ✦",
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
        print("=== render_projects вызван ===")
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        projects = self.manifest.get("projects", {})
        print(f"Найдено проектов: {len(projects)}")
        
        if not projects:
            self.status_label.config(text="❌ Нет проектов в манифесте!")
            return
        
        row_frame = tk.Frame(self.cards_frame, bg=self.bg_dark)
        row_frame.pack(fill=tk.BOTH, expand=True)
        
        for idx, (project_id, project_data) in enumerate(projects.items()):
            print(f"Создаём карточку для: {project_id}")
            self.create_project_card(row_frame, project_id, project_data, idx)
        
        self.status_label.config(text=f"✦ {len(projects)} ПРОЕКТОВ ГОТОВЫ К ЗАПУСКУ")
    
    def create_project_card(self, parent, project_id, project_data, idx):
        """Упрощённая карточка, которая точно отображается"""
        glow_color = project_data.get("color", "#ff2d8a")
        name = project_data.get("name", project_id)
        icon = project_data.get("icon", "📦")
        description = project_data.get("description", "")
        
        # Карточка
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
        
        # Внутренний контейнер
        inner = tk.Frame(card, bg=self.card_bg)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Иконка
        icon_label = tk.Label(
            inner,
            text=icon,
            font=("Segoe UI", 36),
            bg=self.card_bg,
            fg=glow_color
        )
        icon_label.pack(pady=(0, 10))
        
        # Название
        name_label = tk.Label(
            inner,
            text=name,
            font=("Segoe UI", 18, "bold"),
            bg=self.card_bg,
            fg=self.text_primary
        )
        name_label.pack()
        
        # Теги
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
        
        # Описание
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
        
        # Статус
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
        
        # Кнопка запуска
        launch_btn = tk.Button(
            inner,
            text="▶ ЗАПУСТИТЬ",
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
        
        # Эффекты наведения
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
        project_path = project_data.get("path")
        if project_path and os.path.exists(project_path):
            return {"text": "✦ УСТАНОВЛЕН", "color": "#10b981"}
        else:
            return {"text": "✧ НЕ НАЙДЕН", "color": "#ff2d8a"}
    
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
    
    def launch_project(self, project_id):
        project_data = self.manifest["projects"].get(project_id)
        if not project_data:
            messagebox.showerror("Ошибка", f"Проект {project_id} не найден!")
            return
        
        project_path = project_data.get("path")
        if not project_path or not os.path.exists(project_path):
            messagebox.showerror("Ошибка", f"Файл не найден:\n{project_path}")
            return
        
        try:
            self.status_label.config(text=f"🚀 ЗАПУСК {project_data['name']}...")
            if project_data.get("type") == "python":
                subprocess.Popen([sys.executable, project_path], shell=True)
            else:
                subprocess.Popen([project_path], shell=True)
            self.status_label.config(text=f"✦ {project_data['name']} ЗАПУЩЕН")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить {project_data['name']}:\n{str(e)}")
            self.status_label.config(text=f"❌ ОШИБКА ЗАПУСКА {project_data['name']}")
    
    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("✦ НАСТРОЙКИ ✦")
        settings_window.geometry("450x350")
        settings_window.configure(bg=self.bg_medium)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        title = tk.Label(settings_window, text="✦ НАСТРОЙКИ", font=("Segoe UI", 18, "bold"), bg=self.bg_medium, fg=self.text_primary)
        title.pack(pady=25)
        
        frame = tk.Frame(settings_window, bg=self.bg_medium)
        frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        auto_var = tk.BooleanVar(value=self.settings.get("auto_update", True))
        auto_check = tk.Checkbutton(frame, text="Автоматически проверять обновления", variable=auto_var, bg=self.bg_medium, fg=self.text_secondary, selectcolor=self.bg_medium, font=("Segoe UI", 11))
        auto_check.pack(anchor=tk.W, pady=8)
        
        separator = tk.Frame(frame, bg="#2a2a5a", height=1)
        separator.pack(fill=tk.X, pady=10)
        
        def save():
            self.settings["auto_update"] = auto_var.get()
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            settings_window.destroy()
            self.status_label.config(text="✅ НАСТРОЙКИ СОХРАНЕНЫ!")
        
        save_btn = tk.Button(settings_window, text="💾 СОХРАНИТЬ", font=("Segoe UI", 12, "bold"), bg="#ff2d8a", fg="#ffffff", relief=tk.FLAT, padx=30, pady=10, command=save, cursor="hand2")
        save_btn.pack(pady=25)

if __name__ == "__main__":
    root = tk.Tk()
    app = NeoBrainLauncher(root)
    root.mainloop()