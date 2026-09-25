"""
NeoTracker — работа с базой данных (SQLite).

Этот модуль отвечает за:
- создание БД и таблиц
- добавление/чтение/обновление/удаление категорий
- добавление/чтение/обновление/удаление товаров
- автобэкап базы (раз в день)

Все данные хранятся в одном файле: data/warehouse.db
Бэкапы — в data/backups/warehouse_YYYY-MM-DD.db
"""

import sqlite3
import os
import shutil
from datetime import datetime, date


# ============================================================
# ПУТИ
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "warehouse.db")

BACKUP_DIR = os.path.join(DATA_DIR, "backups")
BACKUP_KEEP_DAYS = 14  # сколько последних бэкапов хранить

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


# ============================================================
# ПОДКЛЮЧЕНИЕ
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            price REAL NOT NULL DEFAULT 0,
            description TEXT DEFAULT '',
            no_stock INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# АВТОБЭКАП
# ============================================================

def daily_backup():
    """
    Создаёт один бэкап базы в день в data/backups/.
    Если бэкап на сегодня уже есть — ничего не делает.
    Автоматически удаляет бэкапы старше BACKUP_KEEP_DAYS дней.
    """
    if not os.path.exists(DB_PATH):
        return  # базы ещё нет — нечего бэкапить

    os.makedirs(BACKUP_DIR, exist_ok=True)

    today = date.today().isoformat()
    backup_path = os.path.join(BACKUP_DIR, f"warehouse_{today}.db")

    # Бэкап на сегодня уже есть — выходим
    if os.path.exists(backup_path):
        return

    # Копируем базу
    try:
        shutil.copy2(DB_PATH, backup_path)
    except Exception:
        return  # не ломаем приложение, если бэкап не удался

    # Чистим старые бэкапы (оставляем только BACKUP_KEEP_DAYS последних)
    try:
        backups = sorted(
            f for f in os.listdir(BACKUP_DIR)
            if f.startswith("warehouse_") and f.endswith(".db")
        )
        while len(backups) > BACKUP_KEEP_DAYS:
            old = backups.pop(0)
            os.remove(os.path.join(BACKUP_DIR, old))
    except Exception:
        pass


# ============================================================
# КАТЕГОРИИ
# ============================================================

def get_all_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_category(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_category(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO categories (name, created_at) VALUES (?, ?)",
        (name, datetime.now().isoformat())
    )
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    return category_id


def update_category(category_id, new_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE categories SET name = ? WHERE id = ?",
        (new_name, category_id)
    )
    conn.commit()
    conn.close()


def delete_category(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()


def category_exists(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM categories WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    return row is not None


# ============================================================
# ТОВАРЫ
# ============================================================

def get_products_by_category(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM products WHERE category_id = ? ORDER BY name",
        (category_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_product(category_id, name, quantity=0, price=0.0, description="", no_stock=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products 
        (category_id, name, quantity, price, description, no_stock, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        category_id, name, quantity, price, description,
        1 if no_stock else 0,
        datetime.now().isoformat()
    ))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id


def update_product(product_id, name=None, quantity=None, price=None,
                   description=None, no_stock=None):
    fields = []
    values = []

    if name is not None:
        fields.append("name = ?"); values.append(name)
    if quantity is not None:
        fields.append("quantity = ?"); values.append(quantity)
    if price is not None:
        fields.append("price = ?"); values.append(price)
    if description is not None:
        fields.append("description = ?"); values.append(description)
    if no_stock is not None:
        fields.append("no_stock = ?"); values.append(1 if no_stock else 0)

    if not fields:
        return

    values.append(product_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE products SET {', '.join(fields)} WHERE id = ?",
        values
    )
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def search_products(query, category_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if category_id is not None:
        cursor.execute(
            "SELECT * FROM products WHERE category_id = ? ORDER BY name",
            (category_id,)
        )
    else:
        cursor.execute("SELECT * FROM products ORDER BY name")

    rows = cursor.fetchall()
    conn.close()

    # Фильтрация на стороне Python — корректно работает с русским
    query_lower = query.lower().strip()
    if not query_lower:
        return [dict(row) for row in rows]

    return [
        dict(row) for row in rows
        if query_lower in row["name"].lower()
    ]


# ============================================================
# СТАТИСТИКА
# ============================================================

def get_total_quantity():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM products WHERE no_stock = 0")
    result = cursor.fetchone()[0]
    conn.close()
    return result


def get_total_value():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(quantity * price), 0) FROM products WHERE no_stock = 0")
    result = cursor.fetchone()[0]
    conn.close()
    return result


def get_category_quantity(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COALESCE(SUM(quantity), 0) FROM products WHERE category_id = ? AND no_stock = 0",
        (category_id,)
    )
    result = cursor.fetchone()[0]
    conn.close()
    return result


def get_category_value(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COALESCE(SUM(quantity * price), 0) FROM products WHERE category_id = ? AND no_stock = 0",
        (category_id,)
    )
    result = cursor.fetchone()[0]
    conn.close()
    return result