import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
import subprocess
import shutil

from ui_theme import COLORS, draw_glass_background


class NeoLauncher:
    # ---- Карусель ----
    CARD_W = 320
    CARD_H = 420
    GAP = 50
    HOVER_OFFSET = 12
    HOVER_UNSET_DELAY = 60

    # ---- Сетка ----
    GRID_CARD_W = 280
    GRID_CARD_H = 360
    GRID_GAP_X = 25
    GRID_GAP_Y = 25

    def __init__(self, root):
        self.root = root
        self.root.title("✦ NeoBrain Launcher ✦")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 600)
        self.root.configure(bg=COLORS["bg"])

        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.manifest_path = os.path.join(self.base_dir, "manifest.json")
        self.settings_path = os.path.join(self.base_dir, "launcher_settings.json")

        self.manifest = self.load_manifest()
        self.settings = self.load_settings()

        self.active_index = 0
        self._cards = []

        self._wheel_cooldown = 0
        self._carousel_frame = None
        self._grid_frame = None

        self._hover_index = None
        self._hover_job = None
        self._hover_anim_jobs = {}
        self._base_y = 0

        self._resize_job = None

        self.setup_ui()
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
        default = {"view_mode": "scroll"}
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

    def setup_ui(self):
        # ---- Фоновый canvas ----
        self.bg_canvas = tk.Canvas(
            self.root,
            bg=COLORS["bg"],
            highlightthickness=0
        )
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Контейнер поверх фона
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.place(x=0, y=0, relwidth=1, relheight=1)

        self.root.after(80, self._redraw_background)
        self.root.bind("<Configure>", self._on_resize)

        # ---- Верхняя панель ----
        top_bar = tk.Frame(main, bg=COLORS["bg"])
        top_bar.pack(fill=tk.X, padx=40, pady=(30, 0))

        tk.Label(
            top_bar,
            text="✦  NeoBrain Launcher",
            font=("Segoe UI Light", 34),
            bg=COLORS["bg"],
            fg=COLORS["text"]
        ).pack(side=tk.LEFT)

        self.view_btn = tk.Button(
            top_bar,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["card_top"],
            fg=COLORS["muted"],
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.toggle_view_mode,
            activebackground=COLORS["card_active"],
            activeforeground=COLORS["text"],
            bd=0,
        )
        self.view_btn.pack(side=tk.RIGHT)

        self.status_label = tk.Label(
            main,
            text="✦  СИСТЕМА АКТИВНА",
            font=("Segoe UI", 12),
            bg=COLORS["bg"],
            fg=COLORS["muted"]
        )
        self.status_label.pack(anchor=tk.W, padx=40, pady=(8, 0))

        # Тонкая линия под статусом
        sep = tk.Frame(main, bg=COLORS["separator"], height=1)
        sep.pack(fill=tk.X, padx=40, pady=(12, 0))

        self.cards_container = tk.Frame(main, bg=COLORS["bg"])
        self.cards_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=(20, 0))

        tk.Label(
            main,
            text="✦  ВСЕ ПРОЕКТЫ В ОДНОЙ ПАПКЕ  ✦",
            font=("Segoe UI", 9),
            bg=COLORS["bg"],
            fg=COLORS["dim"]
        ).pack(side=tk.BOTTOM, pady=(0, 15))

        self.root.bind("<Left>", lambda e: self.change_active(-1))
        self.root.bind("<Right>", lambda e: self.change_active(1))
        self.root.bind("<MouseWheel>", self._on_mousewheel)

        self._update_view_btn_text()

    def _redraw_background(self, event=None):
        try:
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            if w < 10 or h < 10:
                return
            draw_glass_background(self.bg_canvas, w, h)
        except Exception:
            pass

    def _on_resize(self, event):
        if event.widget == self.root:
            if self._resize_job is not None:
                try:
                    self.root.after_cancel(self._resize_job)
                except Exception:
                    pass
            self._resize_job = self.root.after(150, self._redraw_background)

    def _update_view_btn_text(self):
        mode = self.settings.get("view_mode", "scroll")
        if mode == "scroll":
            self.view_btn.config(text="↔  Карусель")
        else:
            self.view_btn.config(text="🔲  Сетка")

    def toggle_view_mode(self):
        current = self.settings.get("view_mode", "scroll")
        self.settings["view_mode"] = "grid" if current == "scroll" else "scroll"
        self.save_settings()
        self._update_view_btn_text()
        self.active_index = 0
        self.render_projects()

    # ============================================================
    # РЕНДЕР
    # ============================================================

    def render_projects(self):
        for job in list(self._hover_anim_jobs.values()):
            try:
                self.root.after_cancel(job)
            except Exception:
                pass
        self._hover_anim_jobs = {}
        if self._hover_job is not None:
            try:
                self.root.after_cancel(self._hover_job)
            except Exception:
                pass
            self._hover_job = None

        for w in self.cards_container.winfo_children():
            w.destroy()
        self._cards = []
        self._carousel_frame = None
        self._grid_frame = None
        self._hover_index = None

        projects = self.manifest.get("projects", {})
        if not projects:
            self.status_label.config(text="❌ Нет проектов")
            return

        mode = self.settings.get("view_mode", "scroll")

        if mode == "grid":
            self._render_grid(projects)
        else:
            self._render_scroll(projects)

        self.status_label.config(text=f"✦  {len(projects)} ПРОЕКТОВ ГОТОВЫ К ЗАПУСКУ")

    # ============================================================
    # СЕТКА
    # ============================================================

    def _render_grid(self, projects):
        self._grid_frame = tk.Frame(self.cards_container, bg=COLORS["bg"])
        self._grid_frame.pack(fill=tk.BOTH, expand=True)
        self._grid_frame.update_idletasks()

        items = list(projects.items())
        total = len(items)

        container_w = self._grid_frame.winfo_width()
        container_h = self._grid_frame.winfo_height()
        if container_w <= 1:
            container_w = self.root.winfo_width() - 80
        if container_h <= 1:
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
            self._create_card(self._grid_frame, pid, data, idx,
                              mode="grid", x=x, y=y)

        self.active_index = 0
        self._update_cards_style()

    # ============================================================
    # КАРУСЕЛЬ
    # ============================================================

    def _render_scroll(self, projects):
        self._carousel_frame = tk.Frame(self.cards_container, bg=COLORS["bg"])
        self._carousel_frame.pack(fill=tk.BOTH, expand=True)

        for idx, (pid, data) in enumerate(projects.items()):
            self._create_card(self._carousel_frame, pid, data, idx, mode="scroll")

        self.active_index = 0
        self.root.after(60, self._layout_cards_now)

    def _get_center_x(self):
        try:
            w = self._carousel_frame.winfo_width()
        except Exception:
            w = 0
        if w <= 1:
            w = self.root.winfo_width() - 80
        return w // 2

    def _get_base_y(self):
        try:
            parent_h = self._carousel_frame.winfo_height()
        except Exception:
            parent_h = 0
        if parent_h <= 1:
            parent_h = self.CARD_H + 20
        return max(10, (parent_h - self.CARD_H) // 2)

    def _layout_cards_now(self):
        if not self._cards:
            return

        center = self._get_center_x()
        y = self._get_base_y()
        self._base_y = y

        for i, card_info in enumerate(self._cards):
            offset = i - self.active_index
            x = center + offset * (self.CARD_W + self.GAP) - self.CARD_W // 2

            y_offset = 0
            if i == self._hover_index and i != self.active_index:
                y_offset = -self.HOVER_OFFSET

            frame = card_info["frame"]
            try:
                frame.place(x=x, y=y + y_offset,
                            width=self.CARD_W, height=self.CARD_H)
            except Exception:
                pass

    # ============================================================
    # СКРОЛЛ
    # ============================================================

    def _on_mousewheel(self, event):
        if self.settings.get("view_mode") != "scroll":
            return
        if self._wheel_cooldown > 0:
            return
        delta = event.delta
        if abs(delta) < 1:
            return
        if delta < 0:
            self.change_active(1)
        else:
            self.change_active(-1)
        self._wheel_cooldown = 1
        self.root.after(150, self._reset_wheel_cooldown)

    def _reset_wheel_cooldown(self):
        self._wheel_cooldown = 0

    # ============================================================
    # HOVER
    # ============================================================

    def _bind_hover_recursive(self, widget, idx):
        widget.bind("<Enter>", lambda e, i=idx: self._on_card_enter(i), add="+")
        widget.bind("<Leave>", lambda e, i=idx: self._on_card_leave(i), add="+")
        for child in widget.winfo_children():
            self._bind_hover_recursive(child, idx)

    def _on_card_enter(self, index):
        if self._hover_job is not None:
            try:
                self.root.after_cancel(self._hover_job)
            except Exception:
                pass
            self._hover_job = None

        if self._hover_index == index:
            return

        prev = self._hover_index
        self._hover_index = index

        if prev is not None and prev != index:
            self._animate_card_y(prev, 0)
            self._apply_hover_style(prev, False)

        if index != self.active_index:
            self._animate_card_y(index, -self.HOVER_OFFSET)
        self._apply_hover_style(index, True)

    def _on_card_leave(self, index):
        if self._hover_job is not None:
            try:
                self.root.after_cancel(self._hover_job)
            except Exception:
                pass

        def do_leave():
            if self._hover_index == index:
                self._hover_index = None
                self._animate_card_y(index, 0)
                self._apply_hover_style(index, False)
            self._hover_job = None

        self._hover_job = self.root.after(self.HOVER_UNSET_DELAY, do_leave)

    def _animate_card_y(self, index, delta):
        if index < 0 or index >= len(self._cards):
            return
        card_info = self._cards[index]
        frame = card_info["frame"]

        if self.settings.get("view_mode") == "grid":
            return

        job = self._hover_anim_jobs.get(index)
        if job is not None:
            try:
                self.root.after_cancel(job)
            except Exception:
                pass
            self._hover_anim_jobs[index] = None

        try:
            current_y = frame.winfo_y()
            current_x = frame.winfo_x()
        except Exception:
            return

        base_y = self._base_y if self._base_y else self._get_base_y()
        target_y = base_y + delta

        steps = 8
        step_holder = {"i": 0}

        def tick():
            step_holder["i"] += 1
            t = step_holder["i"] / steps
            te = 1 - (1 - t) ** 2
            y = current_y + (target_y - current_y) * te
            try:
                frame.place_configure(x=current_x, y=int(y))
            except Exception:
                return
            if step_holder["i"] < steps:
                self._hover_anim_jobs[index] = self.root.after(12, tick)
            else:
                self._hover_anim_jobs[index] = None

        tick()

    def _apply_hover_style(self, index, hovered):
        if index < 0 or index >= len(self._cards):
            return
        if index == self.active_index:
            return

        card_info = self._cards[index]
        frame = card_info["frame"]
        inner = card_info["inner"]
        card = card_info["card"]

        if hovered:
            card.config(highlightthickness=1,
                        highlightbackground=COLORS["border_hover"])
        else:
            card.config(highlightthickness=1,
                        highlightbackground=COLORS["border_dim"])

    # ============================================================
    # КАРТОЧКА — СТЕКЛЯННАЯ
    # ============================================================

    def _create_card(self, parent, pid, data, idx, mode="scroll", x=0, y=0):
        color = data.get("color", COLORS["accent_pink"])
        name = data.get("name", pid)
        icon = data.get("icon", "📦")
        desc = data.get("description", "")
        path = data.get("path", "")

        if mode == "grid":
            card_w = self.GRID_CARD_W
            card_h = self.GRID_CARD_H
        else:
            card_w = self.CARD_W
            card_h = self.CARD_H

        # Внешний контейнер
        outer = tk.Frame(parent, bg=COLORS["bg"], bd=0,
                         width=card_w, height=card_h)
        outer.place(x=x, y=y, width=card_w, height=card_h)
        outer.pack_propagate(False)

        # Карточка
        card = tk.Frame(
            outer,
            bg=COLORS["card_top"],
            relief=tk.FLAT,
            bd=0,
            highlightbackground=COLORS["border_dim"],
            highlightthickness=1,
            width=card_w,
            height=card_h
        )
        card.place(x=0, y=0, width=card_w, height=card_h)
        card.pack_propagate(False)

        # Тонкая полоса-«блик» сверху (2px, цвет проекта)
        top_stripe = tk.Frame(card, bg=color, height=2)
        top_stripe.place(x=0, y=0, width=card_w, height=2)

        # Внутренний layout
        inner = tk.Frame(card, bg=COLORS["card_top"])
        inner.pack(fill=tk.BOTH, expand=True, padx=18, pady=(18, 18))

        tk.Label(
            inner,
            text=icon,
            font=("Segoe UI", 28),
            bg=COLORS["card_top"],
            fg=color
        ).pack(pady=(0, 12))

        tk.Label(
            inner,
            text=name,
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["card_top"],
            fg=COLORS["text"],
            wraplength=card_w - 40,
            justify=tk.CENTER
        ).pack()

        if desc:
            tk.Label(
                inner,
                text=desc,
                font=("Segoe UI", 9),
                bg=COLORS["card_top"],
                fg=COLORS["muted"],
                wraplength=card_w - 45,
                justify=tk.CENTER
            ).pack(pady=(6, 8))

        full_path = os.path.join(self.base_dir, path)
        exists = os.path.exists(full_path)
        status_text = "✦ ГОТОВ" if exists else "✧ НЕ НАЙДЕН"
        status_color = COLORS["success"] if exists else COLORS["error"]

        tk.Label(
            inner,
            text=status_text,
            font=("Segoe UI", 10),
            bg=COLORS["card_top"],
            fg=status_color
        ).pack()

        tk.Button(
            inner,
            text="▶  ЗАПУСТИТЬ",
            font=("Segoe UI", 11, "bold"),
            bg=color,
            fg="white",
            relief=tk.FLAT,
            padx=18,
            pady=7,
            command=lambda p=pid: self.launch_project(p),
            cursor="hand2",
            bd=0,
            activebackground=COLORS["card_active"],
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

        self._bind_hover_recursive(card, idx)
        return card_info

    # ============================================================
    # КЛИК / АКТИВНАЯ
    # ============================================================

    def _on_card_click(self, index):
        if index == self.active_index:
            return
        self.active_index = index
        self._update_cards_style()
        if self.settings.get("view_mode") == "scroll":
            self.root.after_idle(self._layout_cards_now)

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
        if self.settings.get("view_mode") == "scroll":
            self.root.after_idle(self._layout_cards_now)

    def _update_cards_style(self):
        for i, c in enumerate(self._cards):
            card = c["card"]
            inner = c["inner"]
            color = c["color"]
            stripe = c["stripe"]

            if i == self.active_index:
                if c.get("_was_active"):
                    continue
                c["_was_active"] = True
                card.config(bg=COLORS["card_active"],
                            highlightthickness=1,
                            highlightbackground=color)
                inner.config(bg=COLORS["card_active"])
                stripe.config(bg=color)
                for child in inner.winfo_children():
                    if isinstance(child, tk.Label):
                        try:
                            child.config(bg=COLORS["card_active"])
                        except Exception:
                            pass
            else:
                if not c.get("_was_active", False):
                    continue
                c["_was_active"] = False
                card.config(bg=COLORS["card_top"],
                            highlightthickness=1,
                            highlightbackground=COLORS["border_dim"])
                inner.config(bg=COLORS["card_top"])
                stripe.config(bg=color)
                for child in inner.winfo_children():
                    if isinstance(child, tk.Label):
                        try:
                            child.config(bg=COLORS["card_top"])
                        except Exception:
                            pass

    # ============================================================
    # ЗАПУСК
    # ============================================================

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
            self.status_label.config(text=f"🚀  ЗАПУСК {data['name']}...")

            if project_id == "neospace":
                os.startfile(path)
                self.root.after(3000, lambda: self.status_label.config(
                    text=f"✦  {data['name']} ЗАПУЩЕН"))
                return

            if data.get("type") == "html":
                import webbrowser
                webbrowser.open(f"file:///{path.replace(os.sep, '/')}")
                self.root.after(2000, lambda: self.status_label.config(
                    text=f"✦  {data['name']} ЗАПУЩЕН"))
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

            self.status_label.config(text=f"✦  {data['name']} ЗАПУЩЕН")
        except Exception as e:
            messagebox.showerror("Error", f"Не удалось запустить {data['name']}:\n{str(e)}")
            self.status_label.config(text=f"❌  ОШИБКА ЗАПУСКА {data['name']}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NeoLauncher(root)
    root.mainloop()