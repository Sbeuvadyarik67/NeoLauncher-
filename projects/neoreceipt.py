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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class NeoReceipt:
    def __init__(self, root):
        self.root = root
        self.root.title("NeoReceipt 2.0 — Генератор чеков")
        self.root.geometry("750x850")
        self.root.configure(bg="#0f1115")
        self.root.minsize(650, 700)

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

        self.font_name = self.register_font()
        self.current_style = "dark"

        self.items = []
        self.preview_window = None
        self.is_live_preview = False

        self.templates = self.load_templates()

        self.setup_ui()

        self.items = [{"name": "", "qty": 1, "price": 0}]
        self.refresh_items_table()

        self.create_templates_folder()
        self.refresh_receipts()
        self.bind_hotkeys()

    # =============================================
    #  ШРИФТЫ
    # =============================================
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
                return font_name
            except:
                continue
        return 'Helvetica'

    # =============================================
    #  ШАБЛОНЫ
    # =============================================
    def load_templates(self):
        if os.path.exists("templates.json"):
            with open("templates.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_templates(self):
        with open("templates.json", "w", encoding="utf-8") as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)

    def save_template(self):
        name = self.entries["company"].get().strip() or "Шаблон"
        self.templates[name] = {
            "company": self.entries["company"].get(),
            "inn": self.entries["inn"].get(),
            "items": self.items
        }
        self.save_templates()
        self.update_template_list()
        messagebox.showinfo("Сохранено", f"Шаблон «{name}» сохранён!")

    def load_selected_template(self, event=None):
        name = self.template_var.get()
        if not name or name not in self.templates:
            return
        tpl = self.templates[name]
        self.entries["company"].delete(0, tk.END)
        self.entries["company"].insert(0, tpl.get("company", ""))
        self.entries["inn"].delete(0, tk.END)
        self.entries["inn"].insert(0, tpl.get("inn", ""))
        if "items" in tpl and tpl["items"]:
            self.items = tpl["items"]
            self.refresh_items_table()

    def update_template_list(self):
        self.template_menu["menu"].delete(0, tk.END)
        for name in self.templates:
            self.template_menu["menu"].add_command(
                label=name,
                command=lambda n=name: self.load_selected_template(None)
            )

    # =============================================
    #  МУЛЬТИ-ТОВАРЫ
    # =============================================
    def add_item_row(self):
        self.items.append({"name": "", "qty": 1, "price": 0})
        self.refresh_items_table()

    def remove_item_row(self, idx):
        if len(self.items) > 1:
            self.items.pop(idx)
            self.refresh_items_table()

    def update_item(self, idx, field, value):
        if idx < len(self.items):
            if field == "qty" or field == "price":
                try:
                    value = int(value) if value else 0
                except:
                    value = 0
            self.items[idx][field] = value
            self.update_total()
            self.update_preview()

    def refresh_items_table(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        header = tk.Frame(self.items_frame, bg=self.colors["bg"])
        header.pack(fill=tk.X)
        tk.Label(header, text="Товар", width=20, anchor=tk.W, bg=self.colors["bg"], fg=self.colors["fg"]).pack(side=tk.LEFT, padx=2)
        tk.Label(header, text="Кол-во", width=8, anchor=tk.W, bg=self.colors["bg"], fg=self.colors["fg"]).pack(side=tk.LEFT, padx=2)
        tk.Label(header, text="Цена", width=10, anchor=tk.W, bg=self.colors["bg"], fg=self.colors["fg"]).pack(side=tk.LEFT, padx=2)
        tk.Label(header, text="", width=4, bg=self.colors["bg"]).pack(side=tk.LEFT)

        for idx, item in enumerate(self.items):
            row = tk.Frame(self.items_frame, bg=self.colors["bg"])
            row.pack(fill=tk.X, pady=1)

            name_entry = tk.Entry(row, width=20, bg=self.colors["input_bg"], fg=self.colors["fg"], relief=tk.FLAT)
            name_entry.insert(0, item["name"])
            name_entry.bind("<KeyRelease>", lambda e, i=idx: self.update_item(i, "name", name_entry.get()))
            name_entry.pack(side=tk.LEFT, padx=2)

            qty_entry = tk.Entry(row, width=8, bg=self.colors["input_bg"], fg=self.colors["fg"], relief=tk.FLAT)
            qty_entry.insert(0, str(item["qty"]))
            qty_entry.bind("<KeyRelease>", lambda e, i=idx: self.update_item(i, "qty", qty_entry.get()))
            qty_entry.pack(side=tk.LEFT, padx=2)

            price_entry = tk.Entry(row, width=10, bg=self.colors["input_bg"], fg=self.colors["fg"], relief=tk.FLAT)
            price_entry.insert(0, str(item["price"]))
            price_entry.bind("<KeyRelease>", lambda e, i=idx: self.update_item(i, "price", price_entry.get()))
            price_entry.pack(side=tk.LEFT, padx=2)

            del_btn = tk.Button(row, text="✖", bg=self.colors["accent"], fg=self.colors["bg"], relief=tk.FLAT,
                                command=lambda i=idx: self.remove_item_row(i), cursor="hand2")
            del_btn.pack(side=tk.LEFT, padx=2)

        self.update_total()

    def update_total(self):
        total = sum(item["qty"] * item["price"] for item in self.items)
        self.total_label.config(text=f"Итого: {total:,} ₽".replace(",", " "))

    # =============================================
    #  LIVE PREVIEW
    # =============================================
    def toggle_live_preview(self):
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
            self.preview_window = None
            self.is_live_preview = False
            self.preview_btn.config(text="👁 Live Preview")
            return

        self.is_live_preview = True
        self.preview_btn.config(text="✖ Закрыть превью")

        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("Live Preview — NeoReceipt")
        self.preview_window.geometry("400x500")
        self.preview_window.configure(bg="#f0f0f0")

        self.preview_text = tk.Text(self.preview_window, wrap=tk.WORD, font=("Arial", 11), bg="#ffffff")
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for key in self.entries:
            self.entries[key].bind("<KeyRelease>", lambda e: self.update_preview())

        self.update_preview()

    def update_preview(self):
        if not self.is_live_preview or not self.preview_window:
            return

        company = self.entries["company"].get().strip() or "ООО Компания"
        inn = self.entries["inn"].get().strip() or "1234567890"
        date = self.entries["date"].get().strip() or datetime.now().strftime("%d.%m.%Y")
        total = sum(item["qty"] * item["price"] for item in self.items)

        preview = f"""
        ═══════════════════════════════════════
               Ч Е К
        ═══════════════════════════════════════

        Компания:  {company}
        ИНН:       {inn}
        Дата:      {date}

        ───────────────────────────────────────
        """

        for item in self.items:
            if item["name"]:
                preview += f"  {item['name']:<20} {item['qty']:>3} x {item['price']:>6} ₽\n"

        preview += f"""
        ───────────────────────────────────────
        ИТОГО:  {total:>10,} ₽
        ═══════════════════════════════════════
        """

        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview)

    # =============================================
    #  PDF
    # =============================================
    def format_number(self, value):
        try:
            digits = ''.join(filter(str.isdigit, str(value)))
            if not digits:
                return str(value)
            return f"{int(digits):,}".replace(",", " ")
        except:
            return str(value)

    def generate_pdf(self):
        try:
            company = self.entries["company"].get().strip()
            inn = self.entries["inn"].get().strip()
            date = self.entries["date"].get().strip()
            total = sum(item["qty"] * item["price"] for item in self.items)

            if not company or not inn or not self.items:
                messagebox.showwarning("Ошибка", "Заполните компанию, ИНН и добавьте хотя бы один товар!")
                return

            filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join("receipts", filename)
            os.makedirs("receipts", exist_ok=True)

            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            font_name = self.font_name

            title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontName=font_name, fontSize=20, textColor=colors.black, alignment=TA_CENTER, spaceAfter=20)
            normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontName=font_name, fontSize=12, spaceAfter=6)

            story = []
            story.append(Paragraph("ЧЕК", title_style))
            story.append(Spacer(1, 6))
            story.append(Paragraph("________________________________", normal_style))
            story.append(Spacer(1, 12))

            story.append(Paragraph(f"<b>Компания:</b> {company}", normal_style))
            story.append(Paragraph(f"<b>ИНН:</b> {inn}", normal_style))
            story.append(Paragraph(f"<b>Дата:</b> {date}", normal_style))
            story.append(Spacer(1, 12))

            data = [["Товар", "Кол-во", "Цена", "Сумма"]]
            for item in self.items:
                if item["name"]:
                    qty = item["qty"]
                    price = item["price"]
                    total_item = qty * price
                    data.append([item["name"], str(qty), f"{price} ₽", f"{total_item} ₽"])

            table = Table(data, colWidths=[6*cm, 2*cm, 2.5*cm, 2.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(table)
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"<b>ИТОГО:</b> {total:,} ₽".replace(",", " "), normal_style))

            doc.build(story)

            abs_path = os.path.abspath(filepath)
            pyperclip.copy(abs_path)
            self.refresh_receipts()
            messagebox.showinfo("Чек создан!", f"Чек сохранён:\n{abs_path}\n\nПуть скопирован в буфер!")
            os.startfile(os.path.abspath("receipts"))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать чек:\n{str(e)}")

    # =============================================
    #  ИСТОРИЯ + ПОИСК
    # =============================================
    def refresh_receipts(self, search=""):
        self.receipt_listbox.delete(0, tk.END)
        try:
            files = sorted(os.listdir("receipts"), reverse=True)
            for f in files:
                if f.endswith(".pdf"):
                    if search.lower() in f.lower():
                        self.receipt_listbox.insert(tk.END, f)
        except:
            pass

    def search_receipts(self, event=None):
        search = self.search_entry.get().strip()
        self.refresh_receipts(search)

    # =============================================
    #  HOTKEYS
    # =============================================
    def bind_hotkeys(self):
        self.root.bind("<Control-n>", lambda e: self.clear_form())
        self.root.bind("<Control-s>", lambda e: self.generate_pdf())
        self.root.bind("<Control-f>", lambda e: self.search_entry.focus())

    def clear_form(self):
        for key in self.entries:
            self.entries[key].delete(0, tk.END)
        self.entries["date"].insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.items = [{"name": "", "qty": 1, "price": 0}]
        self.refresh_items_table()

    # =============================================
    #  ИНТЕРФЕЙС
    # =============================================
    def setup_ui(self):
        c = self.colors
        self.root.configure(bg=c["bg"])

        top = tk.Frame(self.root, bg=c["bg"])
        top.pack(fill=tk.X, pady=(10, 5))

        tk.Label(top, text="🧾 NeoReceipt 2.0", font=("Segoe UI", 18, "bold"), bg=c["bg"], fg=c["accent"]).pack(side=tk.LEFT, padx=20)

        self.template_var = tk.StringVar()
        self.template_var.set("📂 Шаблоны")
        self.template_menu = tk.OptionMenu(top, self.template_var, "📂 Шаблоны", *self.templates.keys(), command=self.load_selected_template)
        self.template_menu.config(bg=c["accent"], fg=c["bg"], relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=10)
        self.template_menu.pack(side=tk.LEFT, padx=5)

        tk.Button(top, text="💾 Сохранить шаблон", bg=c["accent"], fg=c["bg"], relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=10, command=self.save_template, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="➕ Новый", bg=c["accent"], fg=c["bg"], relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=10, command=self.clear_form, cursor="hand2").pack(side=tk.LEFT, padx=5)

        self.preview_btn = tk.Button(top, text="👁 Live Preview", bg="#3a7d5a", fg="white", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=10, command=self.toggle_live_preview, cursor="hand2")
        self.preview_btn.pack(side=tk.RIGHT, padx=20)

        form = tk.Frame(self.root, bg=c["bg"])
        form.pack(padx=30, fill=tk.X)

        fields = [("Компания:", "company"), ("ИНН:", "inn"), ("Дата:", "date")]
        self.entries = {}
        for label_text, key in fields:
            row = tk.Frame(form, bg=c["bg"])
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label_text, width=12, anchor=tk.W, font=("Segoe UI", 11), bg=c["bg"], fg=c["fg"]).pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(row, font=("Segoe UI", 11), bg=c["input_bg"], fg=c["fg"], insertbackground=c["fg"], relief=tk.FLAT, highlightthickness=1, highlightcolor=c["accent"], highlightbackground=c["border"])
            entry.pack(fill=tk.X, padx=5)
            self.entries[key] = entry
            if key == "date":
                entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        tk.Label(form, text="Товары:", font=("Segoe UI", 12, "bold"), bg=c["bg"], fg=c["fg"]).pack(anchor=tk.W, pady=(10, 2))
        self.items_frame = tk.Frame(form, bg=c["bg"])
        self.items_frame.pack(fill=tk.X)

        btn_row = tk.Frame(form, bg=c["bg"])
        btn_row.pack(fill=tk.X, pady=5)
        tk.Button(btn_row, text="➕ Добавить товар", bg=c["accent"], fg=c["bg"], relief=tk.FLAT, font=("Segoe UI", 10), command=self.add_item_row, cursor="hand2").pack(side=tk.LEFT, padx=5)
        self.total_label = tk.Label(btn_row, text="Итого: 0 ₽", font=("Segoe UI", 12, "bold"), bg=c["bg"], fg=c["accent"])
        self.total_label.pack(side=tk.RIGHT, padx=5)

        action_row = tk.Frame(self.root, bg=c["bg"])
        action_row.pack(pady=10)
        tk.Button(action_row, text="📄 Создать PDF", bg=c["accent"], fg=c["bg"], relief=tk.FLAT, font=("Segoe UI", 12, "bold"), padx=30, pady=8, command=self.generate_pdf, cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(action_row, text="📂 Открыть папку", bg=c["accent"], fg=c["bg"], relief=tk.FLAT, font=("Segoe UI", 12, "bold"), padx=30, pady=8, command=lambda: os.startfile(os.path.abspath("receipts")), cursor="hand2").pack(side=tk.LEFT, padx=10)

        search_row = tk.Frame(self.root, bg=c["bg"])
        search_row.pack(fill=tk.X, padx=30, pady=(10, 0))
        tk.Label(search_row, text="🔍 Поиск:", bg=c["bg"], fg=c["fg"], font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_row, bg=c["input_bg"], fg=c["fg"], font=("Segoe UI", 11), relief=tk.FLAT)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_receipts)

        self.receipt_listbox = tk.Listbox(self.root, bg=c["input_bg"], fg=c["fg"], font=("Consolas", 10), relief=tk.FLAT, height=6)
        self.receipt_listbox.pack(fill=tk.X, padx=30, pady=(5, 10))

    def create_templates_folder(self):
        if not os.path.exists("receipts"):
            os.makedirs("receipts")


if __name__ == "__main__":
    root = tk.Tk()
    app = NeoReceipt(root)
    root.mainloop()