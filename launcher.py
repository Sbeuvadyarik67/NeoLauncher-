import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import subprocess
import shutil


class NeoLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("✦ NeoBrain Launcher ✦")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 600)
        self.root.configure(bg="#050510")

        # Определяем базовую папку:
        # - если запущен как .exe — папка рядом с exe
        # - если запущен как .py — папка скрипта
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.manifest_path = os.path.join(self.base_dir, "manifest.json")
        self.manifest = self.load_manifest()

        self.setup_ui()
        self.render_projects()

    def load_manifest(self):
        try:
            if os.path.exists(self.manifest_path):
                with open(self.manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {"projects": {}}

    def setup_ui(self):
        main = tk.Frame(self.root, bg="#050510")
        main.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        tk.Label(
            main,
            text="✦ NeoBrain Launcher",
            font=("Segoe UI", 34, "bold"),
            bg="#050510",
            fg="#f0e8ff"
        ).place(relx=0.03, rely=0.05)

        self.status_label = tk.Label(
            main,
            text="✦ СИСТЕМА АКТИВНА",
            font=("Segoe UI", 12),
            bg="#050510",
            fg="#8a7aaa"
        )
        self.status_label.place(relx=0.03, rely=0.15)

        self.cards_frame = tk.Frame(main, bg="#050510")
        self.cards_frame.place(relx=0, rely=0.23, relwidth=1, relheight=0.7)

        tk.Label(
            main,
            text="✦ ВСЕ ПРОЕКТЫ В ОДНОЙ ПАПКЕ ✦",
            font=("Segoe UI", 9),
            bg="#050510",
            fg="#2a2a5a"
        ).place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def render_projects(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        projects = self.manifest.get("projects", {})
        if not projects:
            self.status_label.config(text="❌ Нет проектов")
            return

        row = tk.Frame(self.cards_frame, bg="#050510")
        row.pack(fill=tk.BOTH, expand=True)

        for idx, (pid, data) in enumerate(projects.items()):
            self.create_card(row, pid, data, idx)

        self.status_label.config(text=f"✦ {len(projects)} ПРОЕКТОВ ГОТОВЫ К ЗАПУСКУ")

    def create_card(self, parent, pid, data, idx):
        color = data.get("color", "#ff2d8a")
        name = data.get("name", pid)
        icon = data.get("icon", "📦")
        desc = data.get("description", "")
        path = data.get("path", "")

        card = tk.Frame(
            parent,
            bg="#0f0f2a",
            relief=tk.FLAT,
            bd=2,
            highlightbackground=color,
            highlightthickness=2,
            width=300,
            height=350
        )
        card.grid(row=0, column=idx, padx=15, pady=10)
        parent.grid_columnconfigure(idx, weight=1)
        card.pack_propagate(False)

        inner = tk.Frame(card, bg="#0f0f2a")
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            inner,
            text=icon,
            font=("Segoe UI", 36),
            bg="#0f0f2a",
            fg=color
        ).pack(pady=(0, 10))

        tk.Label(
            inner,
            text=name,
            font=("Segoe UI", 18, "bold"),
            bg="#0f0f2a",
            fg="#f0e8ff"
        ).pack()

        if desc:
            tk.Label(
                inner,
                text=desc,
                font=("Segoe UI", 10),
                bg="#0f0f2a",
                fg="#8a7aaa",
                wraplength=240,
                justify=tk.CENTER
            ).pack(pady=(5, 10))

        full_path = os.path.join(self.base_dir, path)
        exists = os.path.exists(full_path)
        status_text = "✦ ГОТОВ" if exists else "✧ НЕ НАЙДЕН"
        status_color = "#10b981" if exists else "#ff2d8a"

        tk.Label(
            inner,
            text=status_text,
            font=("Segoe UI", 10),
            bg="#0f0f2a",
            fg=status_color
        ).pack()

        tk.Button(
            inner,
            text="▶ ЗАПУСТИТЬ",
            font=("Segoe UI", 11, "bold"),
            bg=color,
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=lambda p=pid: self.launch_project(p),
            cursor="hand2"
        ).pack(pady=10)

    def launch_project(self, project_id):
        data = self.manifest["projects"].get(project_id)
        if not data:
            messagebox.showerror("Error", f"Проект {project_id} не найден!")
            return

        path = os.path.join(self.base_dir, data.get("path", ""))
        if not os.path.exists(path):
            messagebox.showerror("Error", f"Файл не найден:\n{path}")
            return

        try:
            self.status_label.config(text=f"🚀 ЗАПУСК {data['name']}...")

            # ДЛЯ NEOSPACE ИСПОЛЬЗУЕМ os.startfile (как двойной клик)
            if project_id == "neospace":
                os.startfile(path)
                self.root.after(3000, lambda: self.status_label.config(text=f"✦ {data['name']} ЗАПУЩЕН"))
                return

            if data.get("type") == "python":
                # НАХОДИМ PYTHON В СИСТЕМЕ
                python_exe = shutil.which('python')
                if not python_exe:
                    python_exe = shutil.which('python3')
                if not python_exe:
                    python_exe = 'python'

                # ЗАПУСКАЕМ ПРОЕКТ В ЕГО ПАПКЕ
                project_dir = os.path.dirname(path)

                subprocess.Popen(
                    [python_exe, path],
                    cwd=project_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
            else:
                subprocess.Popen([path], shell=False)

            self.status_label.config(text=f"✦ {data['name']} ЗАПУЩЕН")
        except Exception as e:
            messagebox.showerror("Error", f"Не удалось запустить {data['name']}:\n{str(e)}")
            self.status_label.config(text=f"❌ ОШИБКА ЗАПУСКА {data['name']}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NeoLauncher(root)
    root.mainloop()