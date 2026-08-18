import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import pyperclip

# Подключаем поддержку шрифтов
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class NeoReceipt:
    def __init__(self, root):
        self.root = root
        self.root.title("NeoReceipt — Генератор чеков")
        self.root.geometry("600x790")
        self.root.configure(bg="#0f1115")
        self.root.minsize(500, 700)

        # Цвета по умолчанию (тёмная тема)
        self.colors = {
            "bg": "#0f1115",
            "fg": "#e8f0ff",
            "accent": "#58a6ff",
            "input_bg": "#1c2333",
            "panel_bg": "#161f2a",
            "border": "#2a2a4a",
            "hover": "#2a3a5a",
            "shadow": "black"
        }

        self.current_style = "dark"
        self.font_name = self.register_font()
        self.style_panel_open = False

        self.setup_ui()
        self.create_templates_folder()

    def register_font(self):
        fonts_to_try = [
            ('Arial', 'C:/Windows/Fonts/arial.ttf'),
            ('TimesNewRoman', 'C:/Windows/Fonts/times.ttf'),
            ('Calibri', 'C:/Windows/Fonts/calibri.ttf'),
            ('Tahoma', 'C:/Windows/Fonts/tahoma.ttf'),
            ('Verdana', 'C:/Windows/Fonts/verdana.ttf'),
        ]
        for font_name, font_path in fonts_to_try:
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                print(f"✅ Шрифт '{font_name}' успешно загружен")
                return font_name
            except:
                continue
        print("⚠️ Русские шрифты не найдены! Используется Helvetica")
        return 'Helvetica'

    def create_templates_folder(self):
        if not os.path.exists("templates"):
            os.makedirs("templates")
        if not os.path.exists("receipts"):
            os.makedirs("receipts")

    def format_number(self, value):
        try:
            digits = ''.join(filter(str.isdigit, str(value)))
            if not digits:
                return str(value)
            return f"{int(digits):,}".replace(",", " ")
        except:
            return str(value)

    def get_clean_number(self, key):
        raw = self.entries[key].get().strip()
        cleaned = ''.join(filter(str.isdigit, raw))
        return int(cleaned) if cleaned else 0

    # ========== СТИЛИ ==========

    def apply_style(self, style_name):
        self.current_style = style_name

        if style_name == "dark":
            self.colors = {
                "bg": "#0f1115",
                "fg": "#e8f0ff",
                "accent": "#58a6ff",
                "input_bg": "#1c2333",
                "panel_bg": "#161f2a",
                "border": "#2a2a4a",
                "hover": "#2a3a5a",
                "shadow": "black"
            }
        elif style_name == "light":
            self.colors = {
                "bg": "#f0f2f5",
                "fg": "#1a1a1a",
                "accent": "#3a7d5a",
                "input_bg": "#ffffff",
                "panel_bg": "#e4e8ee",
                "border": "#c8cdd6",
                "hover": "#d5dbe3",
                "shadow": "#c0c0c0"
            }
        elif style_name == "warm":
            self.colors = {
                "bg": "#f5ede4",
                "fg": "#2a1f1a",
                "accent": "#b07a5a",
                "input_bg": "#fffaf2",
                "panel_bg": "#e8ddd0",
                "border": "#ccbbaa",
                "hover": "#dccfc2",
                "shadow": "#b8a898"
            }
        elif style_name == "pastel":
            self.colors = {
                "bg": "#f0f0f5",
                "fg": "#2a2a3a",
                "accent": "#8a7aaa",
                "input_bg": "#fafaff",
                "panel_bg": "#e8e4f0",
                "border": "#c8c0d8",
                "hover": "#d8d0e8",
                "shadow": "#b8b0c8"
            }

        self.update_ui()

    def update_ui(self):
        c = self.colors

        self.root.configure(bg=c["bg"])

        for child in self.root.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=c["bg"])
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label):
                        sub.configure(bg=c["bg"], fg=c["fg"])
                    elif isinstance(sub, tk.Button):
                        if "Стиль" not in sub.cget("text"):
                            sub.configure(bg=c["accent"], fg=c["bg"])
                    elif isinstance(sub, tk.Entry):
                        sub.configure(bg=c["input_bg"], fg=c["fg"])
                    elif isinstance(sub, tk.Listbox):
                        sub.configure(bg=c["input_bg"], fg=c["fg"])

        if hasattr(self, 'style_panel') and self.style_panel.winfo_exists():
            self.style_panel.configure(bg=c["panel_bg"])
            for child in self.style_panel.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=c["panel_bg"])
                    for sub in child.winfo_children():
                        if isinstance(sub, tk.Label):
                            sub.configure(bg=c["panel_bg"], fg=c["fg"])
                        elif isinstance(sub, tk.Button):
                            sub.configure(bg=c["accent"], fg=c["bg"])
                        elif isinstance(sub, tk.Checkbutton):
                            sub.configure(bg=c["panel_bg"], fg=c["fg"])

    # ========== ПАНЕЛЬ СТИЛЕЙ ==========

    def toggle_style_panel(self):
        if self.style_panel_open:
            self.style_panel.destroy()
            self.style_panel_open = False
        else:
            self.show_style_panel()

    def show_style_panel(self):
        c = self.colors
        self.style_panel = tk.Toplevel(self.root)
        self.style_panel.title("🎨 Стиль")
        self.style_panel.geometry("320x420")
        self.style_panel.configure(bg=c["panel_bg"])
        self.style_panel.overrideredirect(True)
        self.style_panel.resizable(False, False)

        x = self.root.winfo_x() + self.root.winfo_width() - 340
        y = self.root.winfo_y() + 60
        self.style_panel.geometry(f"+{x}+{y}")

        tk.Label(
            self.style_panel,
            text="🎨 Выбор стиля",
            font=("Segoe UI", 14, "bold"),
            bg=c["panel_bg"],
            fg=c["fg"]
        ).pack(pady=(15, 5))

        # Стили
        styles = [
            ("🌙 Тёмный", "Классический неон-стиль\nДля работы в тёмное время", "dark"),
            ("☀️ Светлый", "Чистый, минималистичный\nИдеально для утра", "light"),
            ("🌅 Тёплый", "Уютный, мягкий, комфортный\nДля долгой работы", "warm"),
            ("🌿 Пастельный", "Нежный, спокойный, приятный\nГлаза отдыхают", "pastel"),
        ]

        for title, desc, style_name in styles:
            self.create_style_block(self.style_panel, title, desc, style_name)

        tk.Button(
            self.style_panel,
            text="✖ Закрыть",
            font=("Segoe UI", 10),
            bg=c["accent"],
            fg=c["bg"],
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.toggle_style_panel,
            cursor="hand2"
        ).pack(pady=10)

        self.style_panel_open = True

    def create_style_block(self, parent, title, description, style_name):
        c = self.colors

        frame = tk.Frame(parent, bg=c["panel_bg"])
        frame.pack(fill=tk.X, padx=15, pady=4)

        top_row = tk.Frame(frame, bg=c["panel_bg"])
        top_row.pack(fill=tk.X)

        label = tk.Label(
            top_row,
            text=f"▶ {title}",
            font=("Segoe UI", 12),
            bg=c["panel_bg"],
            fg=c["fg"],
            cursor="hand2"
        )
        label.pack(side=tk.LEFT)

        check_var = tk.BooleanVar(value=False)

        def apply_from_check():
            if check_var.get():
                self.apply_style(style_name)
                for child in parent.winfo_children():
                    if isinstance(child, tk.Frame) and child != frame:
                        for sub in child.winfo_children():
                            if isinstance(sub, tk.Frame):
                                for subsub in sub.winfo_children():
                                    if isinstance(subsub, tk.Checkbutton):
                                        subsub.deselect()
            else:
                self.apply_style("dark")

        check_btn = tk.Checkbutton(
            top_row,
            variable=check_var,
            command=apply_from_check,
            bg=c["panel_bg"],
            fg=c["fg"],
            selectcolor=c["panel_bg"],
            cursor="hand2",
            relief=tk.FLAT
        )
        check_btn.pack(side=tk.RIGHT, padx=5)

        desc_frame = tk.Frame(frame, bg=c["panel_bg"])
        desc_frame.pack(fill=tk.X)

        tk.Label(
            desc_frame,
            text=description,
            font=("Segoe UI", 10),
            bg=c["panel_bg"],
            fg=c["fg"],
            justify=tk.LEFT,
            wraplength=260
        ).pack(pady=(5, 5), padx=5)

        desc_frame.pack_forget()
        is_open = False

        def toggle_block():
            nonlocal is_open
            if is_open:
                desc_frame.pack_forget()
                label.config(text=f"▶ {title}")
                is_open = False
            else:
                desc_frame.pack(fill=tk.X)
                label.config(text=f"▼ {title}")
                is_open = True

        label.bind("<Button-1>", lambda e: toggle_block())

    # ========== ОСНОВНОЙ ИНТЕРФЕЙС ==========

    def setup_ui(self):
        c = self.colors

        top_bar = tk.Frame(self.root, bg=c["bg"], height=50)
        top_bar.pack(fill=tk.X, pady=(10, 0))
        top_bar.pack_propagate(False)

        tk.Label(
            top_bar,
            text="NeoReceipt",
            font=("Segoe UI", 20, "bold"),
            bg=c["bg"],
            fg=c["accent"]
        ).pack(side=tk.LEFT, padx=20)

        style_btn = tk.Button(
            top_bar,
            text="🎨 Стиль",
            font=("Segoe UI", 11, "bold"),
            bg=c["accent"],
            fg=c["bg"],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.toggle_style_panel,
            cursor="hand2"
        )
        style_btn.pack(side=tk.RIGHT, padx=20)

        tk.Label(
            self.root,
            text="Создай чек за 30 секунд",
            font=("Segoe UI", 12),
            bg=c["bg"],
            fg=c["fg"]
        ).pack(pady=(5, 15))

        form_frame = tk.Frame(self.root, bg=c["bg"])
        form_frame.pack(padx=30, fill=tk.BOTH, expand=True)

        fields = [
            ("Название компании:", "company"),
            ("ИНН:", "inn"),
            ("Товар/услуга:", "item"),
            ("Количество:", "qty"),
            ("Цена за ед. (₽):", "price"),
            ("Дата:", "date"),
        ]

        self.entries = {}

        for label_text, key in fields:
            tk.Label(
                form_frame,
                text=label_text,
                font=("Segoe UI", 11),
                bg=c["bg"],
                fg=c["fg"]
            ).pack(anchor=tk.W, pady=(10, 2))

            entry = tk.Entry(
                form_frame,
                font=("Segoe UI", 11),
                bg=c["input_bg"],
                fg=c["fg"],
                insertbackground=c["fg"],
                relief=tk.FLAT,
                highlightthickness=1,
                highlightcolor=c["accent"],
                highlightbackground=c["border"]
            )
            entry.pack(fill=tk.X, pady=(0, 5))
            self.entries[key] = entry

            if key == "date":
                entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        tk.Label(
            self.root,
            text="💡 Цифры автоматически форматируются в PDF — пробелы не нужны",
            font=("Segoe UI", 9),
            bg=c["bg"],
            fg="#556688"
        ).pack(pady=(5, 5))

        btn_frame = tk.Frame(self.root, bg=c["bg"])
        btn_frame.pack(pady=10)

        def style_btn(text, cmd, color=None):
            if color is None:
                color = c["accent"]
            btn = tk.Button(
                btn_frame,
                text=text,
                font=("Segoe UI", 12, "bold"),
                bg=color,
                fg=c["bg"],
                relief=tk.FLAT,
                padx=20,
                pady=10,
                cursor="hand2",
                command=cmd
            )
            btn.pack(side=tk.LEFT, padx=8)
            return btn

        style_btn("Создать PDF", self.generate_pdf)
        style_btn("Заполнить пример", self.fill_example)
        style_btn("Открыть папку", self.open_receipts_folder)

        tk.Label(
            self.root,
            text="Последние чеки:",
            font=("Segoe UI", 11, "bold"),
            bg=c["bg"],
            fg=c["fg"]
        ).pack(anchor=tk.W, padx=30, pady=(10, 5))

        self.receipt_listbox = tk.Listbox(
            self.root,
            bg=c["input_bg"],
            fg=c["fg"],
            font=("Consolas", 10),
            relief=tk.FLAT,
            height=5
        )
        self.receipt_listbox.pack(fill=tk.X, padx=30, pady=(0, 10))

        self.refresh_receipts()

    def fill_example(self):
        self.entries["company"].delete(0, tk.END)
        self.entries["company"].insert(0, "ИП Иванов И.И.")
        self.entries["inn"].delete(0, tk.END)
        self.entries["inn"].insert(0, "1234567890")
        self.entries["item"].delete(0, tk.END)
        self.entries["item"].insert(0, "Ремонт ноутбука")
        self.entries["qty"].delete(0, tk.END)
        self.entries["qty"].insert(0, "1")
        self.entries["price"].delete(0, tk.END)
        self.entries["price"].insert(0, "5000")

    def generate_pdf(self):
        try:
            company = self.entries["company"].get().strip()
            inn = self.entries["inn"].get().strip()
            item = self.entries["item"].get().strip()
            qty = self.get_clean_number("qty")
            price = self.get_clean_number("price")
            qty_display = self.format_number(qty)
            price_display = self.format_number(price)
            total = qty * price
            total_display = self.format_number(total)
            date = self.entries["date"].get().strip()

            if not all([company, inn, item, qty > 0, price > 0, date]):
                messagebox.showwarning("Ошибка", "Заполните все поля корректно!")
                return

            filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join("receipts", filename)
            os.makedirs("receipts", exist_ok=True)

            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            font_name = self.font_name

            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Title'],
                fontName=font_name,
                fontSize=20,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=20
            )
            normal_style = ParagraphStyle(
                'NormalStyle',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=12,
                spaceAfter=6
            )

            story = []
            story.append(Paragraph("ЧЕК", title_style))
            story.append(Spacer(1, 6))
            story.append(Paragraph("________________________________", normal_style))
            story.append(Spacer(1, 12))

            details = [
                f"<b>Компания:</b> {company}",
                f"<b>ИНН:</b> {inn}",
                f"<b>Дата:</b> {date}",
                "",
                f"<b>Товар/услуга:</b> {item}",
                f"<b>Количество:</b> {qty_display}",
                f"<b>Цена за ед.:</b> {price_display} ₽",
                "",
                f"<b>ИТОГО:</b> {total_display} ₽",
            ]

            for line in details:
                if line == "":
                    story.append(Spacer(1, 6))
                else:
                    story.append(Paragraph(line, normal_style))

            doc.build(story)

            abs_path = os.path.abspath(filepath)
            pyperclip.copy(abs_path)

            self.refresh_receipts()

            messagebox.showinfo(
                "Чек создан!",
                f"Чек сохранён:\n{abs_path}\n\nПуть скопирован в буфер обмена!"
            )

            os.startfile(os.path.abspath("receipts"))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать чек:\n{str(e)}")

    def refresh_receipts(self):
        self.receipt_listbox.delete(0, tk.END)
        try:
            for f in sorted(os.listdir("receipts"), reverse=True):
                if f.endswith(".pdf"):
                    self.receipt_listbox.insert(tk.END, f)
        except:
            pass

    def open_receipts_folder(self):
        try:
            os.startfile(os.path.abspath("receipts"))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NeoReceipt(root)
    root.mainloop()