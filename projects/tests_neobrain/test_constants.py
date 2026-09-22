"""
Тесты констант NeoBrain: LANGUAGES, PALETTES, STYLES, THEME_PROMPTS.
"""

import pytest
import neobrain


# ============================================================
# LANGUAGES
# ============================================================

class TestLanguages:
    """Тесты словаря LANGUAGES."""

    def test_has_ru_and_en(self):
        assert "ru" in neobrain.LANGUAGES
        assert "en" in neobrain.LANGUAGES

    def test_same_keys_ru_en(self):
        ru_keys = set(neobrain.LANGUAGES["ru"].keys())
        en_keys = set(neobrain.LANGUAGES["en"].keys())
        assert ru_keys == en_keys, f"Разные ключи: {ru_keys ^ en_keys}"

    def test_has_title(self):
        assert "title" in neobrain.LANGUAGES["ru"]
        assert "title" in neobrain.LANGUAGES["en"]

    def test_no_empty_values(self):
        for lang, dict_ in neobrain.LANGUAGES.items():
            for key, value in dict_.items():
                assert value != "", f"{lang}.{key} пустой"


# ============================================================
# PALETTES
# ============================================================

class TestPalettes:
    """Тесты словаря PALETTES."""

    REQUIRED_KEYS = {"bg", "card", "border", "accent", "accent2", "text", "muted",
                     "input_bg", "input_border", "scroll_bg", "scroll_handle",
                     "scroll_hover", "light"}

    def test_not_empty(self):
        assert len(neobrain.PALETTES) > 0

    def test_all_have_required_keys(self):
        for name, palette in neobrain.PALETTES.items():
            missing = self.REQUIRED_KEYS - set(palette.keys())
            assert not missing, f"{name}: нет ключей {missing}"

    def test_light_is_bool(self):
        for name, palette in neobrain.PALETTES.items():
            assert isinstance(palette["light"], bool), f"{name}: light не bool"

    def test_has_light_and_dark(self):
        has_dark = any(not p["light"] for p in neobrain.PALETTES.values())
        has_light = any(p["light"] for p in neobrain.PALETTES.values())
        assert has_dark, "Нет тёмных тем"
        assert has_light, "Нет светлых тем"

    def test_colors_are_hex_or_rgba(self):
        for name, palette in neobrain.PALETTES.items():
            for key in ("bg", "accent", "text"):
                color = palette[key]
                is_hex = color.startswith("#")
                is_rgba = color.startswith("rgba(")
                assert is_hex or is_rgba, f"{name}.{key}='{color}' — не hex и не rgba"


# ============================================================
# STYLES
# ============================================================

class TestStyles:
    """Тесты словаря STYLES."""

    def test_not_empty(self):
        assert len(neobrain.STYLES) > 0

    def test_has_default(self):
        assert "По умолчанию" in neobrain.STYLES

    def test_all_have_required_keys(self):
        required = {"radius", "btn_radius", "send_radius", "font", "font_size", "input_font"}
        for name, style in neobrain.STYLES.items():
            missing = required - set(style.keys())
            assert not missing, f"{name}: нет ключей {missing}"

    def test_sizes_are_ints(self):
        for name, style in neobrain.STYLES.items():
            for key in ("radius", "btn_radius", "send_radius", "font_size", "input_font"):
                assert isinstance(style[key], int), f"{name}.{key} не int"


# ============================================================
# THEME_PROMPTS
# ============================================================

class TestThemePrompts:
    """Тесты словаря THEME_PROMPTS."""

    def test_not_empty(self):
        assert len(neobrain.THEME_PROMPTS) > 0

    def test_all_prompts_non_empty(self):
        for theme, prompt in neobrain.THEME_PROMPTS.items():
            assert prompt, f"Пустой промпт для '{theme}'"
            assert len(prompt) > 10, f"Слишком короткий промпт для '{theme}'"

    def test_all_dark_themes_have_prompts(self):
        for theme, palette in neobrain.PALETTES.items():
            if not palette["light"]:
                assert theme in neobrain.THEME_PROMPTS, \
                    f"Нет промпта для тёмной темы '{theme}'"