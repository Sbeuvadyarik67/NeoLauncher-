import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
import subprocess
import shutil

from ui_theme import THEMES, get_theme, draw_glass_background
from version import __version__


class NeoLauncher:
    GRID_CARD_W = 270
    GRID_CARD_H = 330
    GRID_GAP_X = 22
    GRID_GAP_Y = 22

    def __init__(self, root):
        self.root = root
        self.root.title(f"\u2726 NeoBrain Launcher v{__version__} \u2726")
        self.root.geometry("1200x750")
        self.root.minsize(800, 600)
        self.theme_name = "neon"
        self.root.configure(bg=THEMES[self.theme_name]["bg"])

        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.manifest_path = os.path.join(self.base_dir, "manifest.json")
        self.settings_path = os.path.join(self.base_dir, "launcher_settings.json")

        self.manifest = self.load_manifest()
        self.settings = self.load_settings()
        self.theme_name = self.settings.get("theme", "neon")

        self.active_index = 0
        self._cards = []
        self._grid_frame = None
        self._resize_job = None
        self._entry_anim_jobs = []

        self.setup_ui()
        self._apply_theme()
        self.render_projects()

    # ============================================================
    # ЗАГРУЗКА / СОХРАНЕНИЕ
    # ============================================================

    def load_manifest(self):
        try:
            if os.path.exists(self.manifest_path):
                with open(self.manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"projects": {}}

    def load_settings(self):
        default = {"theme": "neon"}
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
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
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    # ============================================================
    # UI
    # ============================================================

    @property
    def C(self):
        return THEMES[self.theme_name]

    def setup_ui(self):
        # Фон — сплошной на root
        self.root.configure(bg=self.C["bg"])

        main = tk.Frame(self.root, bg=self.C["bg"])
        main.pack(fill=tk.BOTH, expand=True)

        self._main = main

        self.root.bind("<Configure>", self._on_resize)

        # Верхняя панель
        self._top_bar = tk.Frame(main, bg=self.C["bg"])
        self._top_bar.pack(fill=tk.X, padx=40, pady=(30, 0))

        self.title_label = tk.Label(
            self._top_bar,
            text="\u2726  NeoBrain Launcher",
            font=("Segoe UI Light", 34),
            bg=self.C["bg"],
            fg=self.C["text"]
        )
        self.title_label.pack(side=tk.LEFT)

        self.theme_btn = tk.Button(
            self._top_bar,
            text=self._theme_btn_text(),
            font=("Segoe UI", 10, "bold"),
            bg=self.C["card_top"],
            fg=self.C["muted"],
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.toggle_theme,
            activebackground=self.C["card_active"],
            activeforeground=self.C["text"],
            bd=0,
        )
        self.theme_btn.pack(side=tk.RIGHT)

        self.status_label = tk.Label(
            main,
            text="\u2726  \u0421\u0418\u0421\u0422\u0415\u041c\u0410 \u0410\u041a\u0422\u0418\u0412\u041d\u0410",
            font=("Segoe UI", 12),
            bg=self.C["bg"],
            fg=self.C["muted"]
        )
        self.status_label.pack(anchor=tk.W, padx=40, pady=(8, 0))

        self.sep = tk.Frame(main, bg=self.C["separator"], height=1)
        self.sep.pack(fill=tk.X, padx=40, pady=(12, 0))

        self.cards_container = tk.Frame(main, bg=self.C["bg"])
        self.cards_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=(20, 0))

        self.footer_label = tk.Label(
            main,
            text="\u2726  \u0412\u0421\u0415 \u041f\u0420\u041e\u0415\u041a\u0422\u042b \u0412 \u041e\u0414\u041d\u041e\u0419 \u041f\u0410\u041f\u041a\u0415  \u2726",
            font=("Segoe UI", 9),
            bg=self.C["bg"],
            fg=self.C["dim"]
        )
        self.footer_label.pack(side=tk.BOTTOM, pady=(0, 15))

        self.root.bind("<Left>", lambda e: self.change_active(-1))
        self.root.bind("<Right>", lambda e: self.change_active(1))

    def _theme_btn_text(self):
        return f"\U0001f3a8  {self.theme_name.capitalize()}"

    def _mute_for_claude(self, hex_color):
        """Приглушает яркий цвет проекта под Claude-тему."""
        h = hex_color.lstrip("#")
        try:
            r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        except Exception:
            return hex_color

        gray = (r + g + b) // 3
        mix_gray = 0.30

        r2 = int(r * (1 - mix_gray) + gray * mix_gray)
        g2 = int(g * (1 - mix_gray) + gray * mix_gray)
        b2 = int(b * (1 - mix_gray) + gray * mix_gray)

        darken = 0.88
        r2 = int(r2 * darken)
        g2 = int(g2 * darken)
        b2 = int(b2 * darken)

        return f"#{r2:02x}{g2:02x}{b2:02x}"

    def _on_resize(self, event):
        if event.widget == self.root:
            if self._resize_job is not None:
                try:
                    self.root.after_cancel(self._resize_job)
                except Exception:
                    pass
            self._resize_job = self.root.after(150, self._on_resize_render)

    def _on_resize_render(self):
        """Перерендер при ресайзе."""
        self.render_projects()

    def toggle_theme(self):
        self.theme_name = "claude" if self.theme_name == "neon" else "neon"
        self.settings["theme"] = self.theme_name
        self.save_settings()
        self._apply_theme()

    def _apply_theme(self):
        """Переключает все цвета интерфейса на новую тему."""
        c = self.C

        self.root.configure(bg=c["bg"])
        self._main.config(bg=c["bg"])
        self._top_bar.config(bg=c["bg"])   # ← ФИКС: верхняя панель

        self.title_label.config(bg=c["bg"], fg=c["text"])
        self.status_label.config(bg=c["bg"], fg=c["muted"])
        self.footer_label.config(bg=c["bg"], fg=c["dim"])
        self.theme_btn.config(text=self._theme_btn_text(),
                             bg=c["card_top"], fg=c["muted"],
                             activebackground=c["card_active"],
                             activeforeground=c["text"])
        self.sep.config(bg=c["separator"])
        self.cards_container.config(bg=c["bg"])

        self.render_projects()

    # ============================================================
    # РЕНДЕР
    # ============================================================

    def render_projects(self):
        for w in self.cards_container.winfo_children():
            w.destroy()
        for job in self._entry_anim_jobs:
            try:
                self.root.after_cancel(job)
            except Exception:
                pass
        self._entry_anim_jobs = []
        self._cards = []
        self._grid_frame = None

        projects = self.manifest.get("projects", {})
        if not projects:
            self.status_label.config(text="\u274c \u041d\u0435\u0442 \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432")
            return

        # Откладываем рендер — чтобы контейнер получил реальные размеры
        self.root.after(30, lambda: self._render_grid(projects))

        self.status_label.config(
            text=f"\u2726  {len(projects)} \u041f\u0420\u041e\u0415\u041a\u0422\u041e\u0412 \u0413\u041e\u0422\u041e\u0412\u042b \u041a \u0417\u0410\u041f\u0423\u0421\u041a\u0423")

    # ============================================================
    # СЕТКА
    # ============================================================

    def _render_grid(self, projects):
        self._grid_frame = tk.Frame(self.cards_container, bg=self.C["bg"])
        self._grid_frame.pack(fill=tk.BOTH, expand=True)
        self._grid_frame.update_idletasks()

        items = list(projects.items())
        total = len(items)

        # Получаем РЕАЛЬНЫЕ размеры контейнера
        container_w = self.cards_container.winfo_width()
        container_h = self.cards_container.winfo_height()

        # Fallback — если ещё не отрисовано
        if container_w <= 50:
            container_w = self.root.winfo_width() - 80
        if container_h <= 50:
            container_h = self.root.winfo_height() - 200

        card_w = self.GRID_CARD_W
        card_h = self.GRID_CARD_H
        gap_x = self.GRID_GAP_X
        gap_y = self.GRID_GAP_Y

        cols = max(1, (container_w + gap_x) // (card_w + gap_x))
        rows = (total + cols - 1) // cols

        total_block_w = cols * card_w + (cols - 1) * gap_x
        total_block_h = rows * card_h + (rows - 1) * gap_y

        left_offset = max(0, (container_w - total_block_w) // 2)
        top_offset = max(0, (container_h - total_block_h) // 2)

        for idx, (pid, data) in enumerate(items):
            row = idx // cols
            col = idx % cols
            x = left_offset + col * (card_w + gap_x)
            y = top_offset + row * (card_h + gap_y)
            self._create_card(self._grid_frame, pid, data, idx, x=x, y=y)

        self.active_index = 0
        self._update_cards_style()

        self.root.after(80, lambda: self._animate_entry())

    # ============================================================
    # АНИМАЦИЯ ВЪЕЗДА
    # ============================================================

    def _animate_entry(self):
        """Каскадный въезд карточек снизу."""
        if not self._cards:
            return

        for i, card_info in enumerate(self._cards):
            frame = card_info["frame"]
            try:
                target_y = int(frame.place_info().get("y", 0))
            except Exception:
                continue

            delay = i * 30

            def animate_one(f=frame, ty=target_y):
                try:
                    start_y = ty + 40
                    steps = 18
                    holder = {"step": 0, "job": None}

                    f.place(y=start_y)

                    def tick():
                        holder["step"] += 1
                        t = holder["step"] / steps
                        te = 1 - (1 - t) ** 3
                        y = start_y + (ty - start_y) * te
                        try:
                            f.place_configure(y=int(y))
                        except Exception:
                            return
                        if holder["step"] < steps:
                            holder["job"] = self.root.after(10, tick)

                    holder["job"] = self.root.after(0, tick)
                    self._entry_anim_jobs.append(holder["job"])
                except Exception:
                    pass

            job = self.root.after(delay, animate_one)
            self._entry_anim_jobs.append(job)

    # ============================================================
    # КАРТОЧКА
    # ============================================================

    def _create_card(self, parent, pid, data, idx, x=0, y=0):
        c = self.C
        raw_color = data.get("color", c["accent_pink"])
        if self.theme_name == "claude":
            color = self._mute_for_claude(raw_color)
        else:
            color = raw_color

        name = data.get("name", pid)
        icon = data.get("icon", "\U0001f4e6")
        desc = data.get("description", "")
        path = data.get("path", "")

        card_w = self.GRID_CARD_W
        card_h = self.GRID_CARD_H

        outer = tk.Frame(parent, bg=c["bg"], bd=0, width=card_w, height=card_h)
        outer.place(x=x, y=y, width=card_w, height=card_h)
        outer.pack_propagate(False)

        card = tk.Frame(
            outer,
            bg=c["card_top"],
            relief=tk.FLAT,
            bd=0,
            highlightbackground=c["border_dim"],
            highlightthickness=1,
            width=card_w,
            height=card_h
        )
        card.place(x=0, y=0, width=card_w, height=card_h)
        card.pack_propagate(False)

        top_stripe = tk.Frame(card, bg=color, height=3)
        top_stripe.place(x=0, y=0, width=card_w, height=3)

        inner = tk.Frame(card, bg=c["card_top"])
        inner.pack(fill=tk.BOTH, expand=True, padx=18, pady=(18, 18))

        tk.Label(
            inner,
            text=icon,
            font=("Segoe UI", 28),
            bg=c["card_top"],
            fg=color
        ).pack(pady=(0, 12))

        tk.Label(
            inner,
            text=name,
            font=("Segoe UI", 16, "bold"),
            bg=c["card_top"],
            fg=c["text"],
            wraplength=card_w - 40,
            justify=tk.CENTER
        ).pack()

        # === ВЕРСИЯ ===
        version_text = data.get("version", "")
        if version_text:
            tk.Label(
                inner,
                text=f"v{version_text}",
                font=("Segoe UI", 9),
                bg=c["card_top"],
                fg=c["dim"],
                justify=tk.CENTER
            ).pack(pady=(2, 4))

        if desc:
            tk.Label(
                inner,
                text=desc,
                font=("Segoe UI", 9),
                bg=c["card_top"],
                fg=c["muted"],
                wraplength=card_w - 45,
                justify=tk.CENTER
            ).pack(pady=(6, 8))

        full_path = os.path.join(self.base_dir, path)
        exists = os.path.exists(full_path)
        status_text = "\u2726 \u0413\u041e\u0422\u041e\u0412" if exists else "\u2727 \u041d\u0415 \u041d\u0410\u0419\u0414\u0415\u041d"
        status_color = c["success"] if exists else c["error"]

        tk.Label(
            inner,
            text=status_text,
            font=("Segoe UI", 10),
            bg=c["card_top"],
            fg=status_color
        ).pack()

        tk.Button(
            inner,
            text="\u25b6  \u0417\u0410\u041f\u0423\u0421\u0422\u0418\u0422\u042c",
            font=("Segoe UI", 11, "bold"),
            bg=color,
            fg="white",
            relief=tk.FLAT,
            padx=18,
            pady=7,
            command=lambda p=pid: self.launch_project(p),
            cursor="hand2",
            bd=0,
            activebackground=c["card_active"],
            activeforeground="white",
        ).pack(pady=10)

        outer.bind("<Button-1>", lambda e, i=idx: self._on_card_click(i))
        card.bind("<Button-1>", lambda e, i=idx: self._on_card_click(i))

        card_info = {
            "frame": outer,
            "card": card,
            "inner": inner,
            "stripe": top_stripe,
            "pid": pid,
            "color": color,
            "index": idx,
        }
        self._cards.append(card_info)
        return card_info

    # ============================================================
    # КЛИК / АКТИВНАЯ КАРТОЧКА
    # ============================================================

    def _on_card_click(self, index):
        if index == self.active_index:
            return
        self.active_index = index
        self._update_cards_style()

    def change_active(self, delta):
        if not self._cards:
            return
        new_index = self.active_index + delta
        if new_index < 0:
            new_index = 0
        if new_index >= len(self._cards):
            new_index = len(self._cards) - 1
        if new_index == self.active_index:
            return
        self.active_index = new_index
        self._update_cards_style()

    def _update_cards_style(self):
        for i, ci in enumerate(self._cards):
            card = ci["card"]
            inner = ci["inner"]
            color = ci["color"]
            stripe = ci["stripe"]
            c = self.C

            # ← ФИКС: рамка ВСЕГДА одинаковая — без "щупанья" краёв
            if i == self.active_index:
                card.config(bg=c["card_active"],
                            highlightthickness=1,
                            highlightbackground=c["border_dim"])
                inner.config(bg=c["card_active"])
                stripe.config(bg=color)
                for child in inner.winfo_children():
                    if isinstance(child, tk.Label):
                        try:
                            child.config(bg=c["card_active"])
                        except Exception:
                            pass
            else:
                card.config(bg=c["card_top"],
                            highlightthickness=1,
                            highlightbackground=c["border_dim"])
                inner.config(bg=c["card_top"])
                stripe.config(bg=color)
                for child in inner.winfo_children():
                    if isinstance(child, tk.Label):
                        try:
                            child.config(bg=c["card_top"])
                        except Exception:
                            pass

    # ============================================================
    # ЗАПУСК
    # ============================================================

    def launch_project(self, project_id):
        data = self.manifest["projects"].get(project_id)
        if not data:
            messagebox.showerror("Error", f"\u041f\u0440\u043e\u0435\u043a\u0442 {project_id} \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d!")
            return

        path = os.path.join(self.base_dir, data.get("path", ""))
        if not os.path.exists(path):
            messagebox.showerror("Error", f"\u0424\u0430\u0439\u043b \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d:\n{path}")
            return

        try:
            self.status_label.config(text=f"\U0001f680  \u0417\u0410\u041f\u0423\u0421\u041a {data['name']}...")

            if project_id == "neospace":
                os.startfile(path)
                self.root.after(3000, lambda: self.status_label.config(
                    text=f"\u2726  {data['name']} \u0417\u0410\u041f\u0423\u0429\u0415\u041d"))
                return

            if data.get("type") == "html":
                import webbrowser
                webbrowser.open(f"file:///{path.replace(os.sep, '/')}")
                self.root.after(2000, lambda: self.status_label.config(
                    text=f"\u2726  {data['name']} \u0417\u0410\u041f\u0423\u0429\u0415\u041d"))
                return

            if data.get("type") == "python":
                python_exe = shutil.which('python') or shutil.which('python3') or 'python'
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

            self.status_label.config(text=f"\u2726  {data['name']} \u0417\u0410\u041f\u0423\u0429\u0415\u041d")
        except Exception as e:
            messagebox.showerror("Error", f"\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0437\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c {data['name']}:\n{str(e)}")
            self.status_label.config(text=f"\u274c  \u041e\u0428\u0418\u0411\u041a\u0410 \u0417\u0410\u041f\u0423\u0421\u041a\u0410 {data['name']}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NeoLauncher(root)
    root.mainloop()