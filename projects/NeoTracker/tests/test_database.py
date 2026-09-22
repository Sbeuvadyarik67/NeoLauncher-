"""
Тесты для database.py — категории, товары, поиск, статистика.
"""

import pytest


# ============================================================
# КАТЕГОРИИ — CRUD
# ============================================================

class TestCategories:
    """Тесты для работы с категориями."""

    def test_add_category(self, test_db):
        cat_id = test_db.add_category("Продукты")
        assert cat_id is not None
        assert isinstance(cat_id, int)

    def test_get_all_categories_empty(self, test_db):
        assert test_db.get_all_categories() == []

    def test_get_all_categories(self, test_db):
        test_db.add_category("Продукты")
        test_db.add_category("Электроника")

        cats = test_db.get_all_categories()
        assert len(cats) == 2
        assert cats[0]["name"] == "Продукты"
        assert cats[1]["name"] == "Электроника"

    def test_get_category_by_id(self, test_db):
        cat_id = test_db.add_category("Продукты")
        cat = test_db.get_category(cat_id)

        assert cat is not None
        assert cat["name"] == "Продукты"
        assert cat["id"] == cat_id

    def test_get_category_not_exists(self, test_db):
        assert test_db.get_category(9999) is None

    def test_update_category(self, test_db):
        cat_id = test_db.add_category("Продукты")
        test_db.update_category(cat_id, "Еда")

        cat = test_db.get_category(cat_id)
        assert cat["name"] == "Еда"

    def test_delete_category(self, test_db):
        cat_id = test_db.add_category("Продукты")
        test_db.delete_category(cat_id)

        assert test_db.get_category(cat_id) is None
        assert test_db.get_all_categories() == []

    def test_category_exists(self, test_db):
        test_db.add_category("Продукты")

        assert test_db.category_exists("Продукты") is True
        assert test_db.category_exists("Электроника") is False


# ============================================================
# ТОВАРЫ — CRUD
# ============================================================

class TestProducts:
    """Тесты для работы с товарами."""

    def test_add_product(self, test_db, sample_category):
        prod_id = test_db.add_product(
            category_id=sample_category,
            name="Мышь",
            quantity=10,
            price=1500,
        )
        assert prod_id is not None
        assert isinstance(prod_id, int)

    def test_get_product(self, test_db, sample_product):
        prod = test_db.get_product(sample_product)

        assert prod is not None
        assert prod["name"] == "Компьютер"
        assert prod["quantity"] == 5
        assert prod["price"] == 50000

    def test_get_products_by_category(self, test_db, sample_category):
        test_db.add_product(sample_category, "Мышь", 10, 1500)
        test_db.add_product(sample_category, "Монитор", 3, 15000)

        prods = test_db.get_products_by_category(sample_category)
        assert len(prods) == 2

    def test_update_product(self, test_db, sample_product):
        test_db.update_product(sample_product, name="Ноутбук", price=70000)

        prod = test_db.get_product(sample_product)
        assert prod["name"] == "Ноутбук"
        assert prod["price"] == 70000

    def test_delete_product(self, test_db, sample_product):
        test_db.delete_product(sample_product)
        assert test_db.get_product(sample_product) is None

    def test_no_stock_flag(self, test_db, sample_category):
        prod_id = test_db.add_product(
            sample_category, "Клавиатура", quantity=0, price=2000, no_stock=True
        )
        prod = test_db.get_product(prod_id)
        assert prod["no_stock"] == 1

    def test_delete_category_cascade(self, test_db, sample_category, sample_product):
        assert test_db.get_product(sample_product) is not None

        test_db.delete_category(sample_category)

        assert test_db.get_product(sample_product) is None


# ============================================================
# ПОИСК
# ============================================================

class TestSearch:
    """Тесты поиска товаров."""

    def test_search_by_name(self, test_db, sample_category):
        test_db.add_product(sample_category, "Компьютер", 5, 50000)
        test_db.add_product(sample_category, "Монитор", 3, 15000)

        results = test_db.search_products("Комп")
        assert len(results) == 1
        assert results[0]["name"] == "Компьютер"

    def test_search_partial(self, test_db, sample_category):
        test_db.add_product(sample_category, "Компьютер", 5, 50000)
        test_db.add_product(sample_category, "Монитор", 3, 15000)
        test_db.add_product(sample_category, "Мышь", 10, 1500)

        results = test_db.search_products("м")
        names = [r["name"] for r in results]
        assert "Компьютер" in names
        assert "Монитор" in names
        assert "Мышь" in names

    def test_search_no_results(self, test_db, sample_category):
        test_db.add_product(sample_category, "Компьютер", 5, 50000)

        results = test_db.search_products("xyz")
        assert results == []

    def test_search_in_category(self, test_db):
        cat1 = test_db.add_category("Электроника")
        cat2 = test_db.add_category("Продукты")

        test_db.add_product(cat1, "Яблоко", 10, 50)
        test_db.add_product(cat2, "Яблоко", 5, 30)

        results = test_db.search_products("Яблоко", category_id=cat1)
        assert len(results) == 1
        assert results[0]["category_id"] == cat1


# ============================================================
# СТАТИСТИКА
# ============================================================

class TestStatistics:
    """Тесты подсчёта сумм и количеств."""

    def test_total_quantity_empty(self, test_db):
        assert test_db.get_total_quantity() == 0

    def test_total_quantity(self, test_db, sample_category):
        test_db.add_product(sample_category, "Мышь", 10, 1500)
        test_db.add_product(sample_category, "Монитор", 3, 15000)

        assert test_db.get_total_quantity() == 13

    def test_total_value(self, test_db, sample_category):
        test_db.add_product(sample_category, "Мышь", 10, 1500)
        test_db.add_product(sample_category, "Монитор", 3, 15000)

        assert test_db.get_total_value() == 60000

    def test_total_excludes_no_stock(self, test_db, sample_category):
        test_db.add_product(sample_category, "Мышь", 10, 1500)
        test_db.add_product(sample_category, "Клавиатура", 0, 2000, no_stock=True)

        assert test_db.get_total_quantity() == 10
        assert test_db.get_total_value() == 15000

    def test_category_quantity(self, test_db):
        cat1 = test_db.add_category("Электроника")
        cat2 = test_db.add_category("Продукты")

        test_db.add_product(cat1, "Мышь", 10, 1500)
        test_db.add_product(cat2, "Хлеб", 20, 50)

        assert test_db.get_category_quantity(cat1) == 10
        assert test_db.get_category_quantity(cat2) == 20

    def test_category_value(self, test_db, sample_category):
        test_db.add_product(sample_category, "Мышь", 10, 1500)
        test_db.add_product(sample_category, "Монитор", 3, 15000)

        assert test_db.get_category_value(sample_category) == 60000