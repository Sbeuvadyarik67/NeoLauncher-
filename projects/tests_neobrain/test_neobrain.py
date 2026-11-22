"""
Тесты для NeoBrain v8.3 — проверка целостности кода и словарей.

Обновлено под v8.3 (минимализм): убраны проверки классов и словарей,
которые больше не существуют (OllamaIndicator, SystemMessageBubble,
STYLE_MIGRATION, старый формат BACKGROUNDS).
"""

import pytest
import neobrain


# ============================================================
# ТЕСТ 1: Импорт без синтаксических ошибок
# ============================================================
def test_import_neobrain():
    """Модуль должен импортироваться без SyntaxError и NameError."""
    assert neobrain is not None
    assert hasattr(neobrain, "NeoBrainChat")
    assert hasattr(neobrain, "MessageBubble")


# ============================================================
# ТЕСТ 2: Ключи словарей чистые (без пробелов)
# ============================================================
def test_languages_keys_clean():
    """Ключи в LANGUAGES не должны содержать пробелов на концах."""
    for lang in ("ru", "en"):
        assert lang in neobrain.LANGUAGES, f"Язык '{lang}' не найден в LANGUAGES"
        for key in neobrain.LANGUAGES[lang]:
            assert (
                key == key.strip()
            ), f"Ключ '{key}' в LANGUAGES['{lang}'] содержит пробелы"


def test_palettes_keys_clean():
    """Ключи в PALETTES не должны содержать пробелов."""
    required = [
        "bg",
        "card",
        "border",
        "accent",
        "accent2",
        "text",
        "muted",
        "input_bg",
        "input_border",
        "light",
    ]
    for name, palette in neobrain.PALETTES.items():
        assert name == name.strip(), f"Название палитры '{name}' содержит пробелы"
        for key in required:
            assert key in palette, f"Ключ '{key}' отсутствует в палитре '{name}'"


def test_styles_keys_clean():
    """Ключи в STYLES не должны содержать пробелов."""
    required = [
        "radius",
        "btn_radius",
        "send_radius",
        "font",
        "font_size",
        "input_font",
    ]
    for name, style in neobrain.STYLES.items():
        assert name == name.strip(), f"Название стиля '{name}' содержит пробелы"
        for key in required:
            assert key in style, f"Ключ '{key}' отсутствует в стиле '{name}'"


def test_theme_prompts_keys_clean():
    """Ключи в THEME_PROMPTS должны совпадать с ключами PALETTES."""
    for key in neobrain.THEME_PROMPTS:
        assert (
            key in neobrain.PALETTES
        ), f"Ключ '{key}' в THEME_PROMPTS не найден в PALETTES"


# ============================================================
# ТЕСТ 3: Dunder-методы (__init__) существуют
# ============================================================
def test_dunder_init_methods():
    """У основных классов должен быть __init__."""
    classes_to_check = [
        neobrain.NeoBrainChat,
        neobrain.MessageBubble,
    ]
    for cls in classes_to_check:
        assert hasattr(cls, "__init__"), f"У класса {cls.__name__} нет __init__"


# ============================================================
# ТЕСТ 4: Точка входа (__name__ == "__main__")
# ============================================================
def test_main_guard_exists():
    """В модуле должна быть проверка __name__ == '__main__'."""
    import inspect

    source = inspect.getsource(neobrain)
    assert "__name__" in source, "В модуле не найдена проверка __name__"
    assert (
        '"__main__"' in source or "'__main__'" in source
    ), "В модуле не найдена строка '__main__'"


# ============================================================
# ТЕСТ 5: QSS генерируется корректно
# ============================================================
def test_build_qss():
    """build_qss должна возвращать валидную строку стилей."""
    qss = neobrain.build_qss("🌆 Неон", "По умолчанию")
    assert len(qss) > 500, "QSS слишком короткий"
    assert "QPushButton" in qss
    # Проверяем, что нет сломанных селекторов с пробелами
    assert "QWidg et" not in qss, "В QSS найден сломанный селектор 'QWidg et'"
    assert "QPushBu tton" not in qss, "В QSS найден сломанный селектор 'QPushBu tton'"


def test_build_qss_all_palettes():
    """build_qss должна работать для всех палитр и стилей."""
    for palette_name in neobrain.PALETTES:
        for style_name in neobrain.STYLES:
            qss = neobrain.build_qss(palette_name, style_name)
            assert len(qss) > 100, f"QSS пустой для {palette_name} + {style_name}"


# ============================================================
# ТЕСТ 6: Утилиты работают
# ============================================================
def test_safe_name():
    """_safe_name должна корректно очищать имена."""
    assert neobrain._safe_name("Lina") == "Lina"
    assert neobrain._safe_name("My Character") == "My Character"
    assert neobrain._safe_name("Test@#$%") == "Test"
    assert neobrain._safe_name("") == ""
    assert neobrain._safe_name("  spaces  ") == "spaces"


def test_get_effective_palette():
    """get_effective_palette должна возвращать полный словарь."""
    p = neobrain.get_effective_palette("🌆 Неон", "По умолчанию")
    assert "accent" in p
    assert p["accent"] == "#ff2d8a"

    p_terminal = neobrain.get_effective_palette("🌆 Неон", "💻 Terminal")
    assert p_terminal["accent"] == "#00ff00"

    p_glass = neobrain.get_effective_palette("🌆 Неон", "🪟 Glass")
    assert p_glass["bg"] == "#1a1a2e"


# ============================================================
# ТЕСТ 7: Словари переводов полные
# ============================================================
def test_languages_ru_values_valid():
    """Все значения русского словаря — непустые строки."""
    for key, value in neobrain.LANGUAGES["ru"].items():
        assert isinstance(
            value, str
        ), f"Значение ключа '{key}' в LANGUAGES['ru'] не строка"
        assert value.strip(), f"Пустое значение у ключа '{key}' в LANGUAGES['ru']"


def test_languages_en_has_all_keys():
    """Английский словарь должен содержать те же ключи, что и русский."""
    ru_keys = set(neobrain.LANGUAGES["ru"].keys())
    en_keys = set(neobrain.LANGUAGES["en"].keys())
    missing = ru_keys - en_keys
    assert not missing, f"В английском переводе отсутствуют ключи: {missing}"


# ============================================================
# ТЕСТ 8: Фоны
# ============================================================
# Примечание: в v8.3 фоны устроены иначе, чем раньше, — тест на их
# структуру добавим, сверив реальную структуру по коду neobrain.py.
