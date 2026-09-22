"""
Pytest — фикстуры для тестов NeoTracker.

Главная фикстура test_db:
- создаёт ИЗОЛИРОВАННУЮ тестовую БД в tmp_path
- патчит database.DB_PATH и database.DATA_DIR
- гарантирует, что рабочая data/warehouse.db не тронется
"""

import sys
import os
from pathlib import Path

import pytest

# Корень проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """
    Создаёт изолированную тестовую БД.

    - tmp_path — временная папка от pytest (уникальная для каждого теста)
    - monkeypatch — подменяет пути в database.py
    """
    import database as db

    # Пути к тестовой БД
    test_data_dir = tmp_path / "data"
    test_data_dir.mkdir()
    test_db_path = test_data_dir / "warehouse_test.db"

    # Патчим константы
    monkeypatch.setattr(db, "DATA_DIR", str(test_data_dir))
    monkeypatch.setattr(db, "DB_PATH", str(test_db_path))

    # Создаём таблицы
    db.init_db()

    yield db


@pytest.fixture
def sample_category(test_db):
    """Создаёт тестовую категорию 'Электроника' и возвращает её id."""
    cat_id = test_db.add_category("Электроника")
    return cat_id


@pytest.fixture
def sample_product(test_db, sample_category):
    """Создаёт тестовый товар в категории 'Электроника'."""
    prod_id = test_db.add_product(
        category_id=sample_category,
        name="Компьютер",
        quantity=5,
        price=50000,
        description="Intel i7, 16 GB RAM",
        no_stock=False,
    )
    return prod_id