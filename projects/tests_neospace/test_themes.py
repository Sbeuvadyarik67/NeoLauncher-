"""
Тесты тем NeoSpace OS.
"""

import pytest
import neospace


class TestThemeColors:
    """Тесты get_theme_colors."""

    def test_returns_dict(self):
        colors = neospace.get_theme_colors("neon")
        assert isinstance(colors, dict)

    def test_has_required_keys(self):
        required = {"bg", "bg_light", "fg", "accent", "taskbar", "window_bg"}
        colors = neospace.get_theme_colors("neon")
        missing = required - set(colors.keys())
        assert not missing, f"Нет ключей: {missing}"

    def test_unknown_theme_fallback(self):
        """Неизвестная тема → neon."""
        colors = neospace.get_theme_colors("НЕ СУЩЕСТВУЕТ")
        neon = neospace.get_theme_colors("neon")
        assert colors["accent"] == neon["accent"]

    def test_all_themes_have_category(self):
        for theme in neospace.get_serious_themes() + neospace.get_beautiful_themes():
            colors = neospace.get_theme_colors(theme)
            assert "category" in colors, f"{theme}: нет category"
            assert colors["category"] in ("serious", "beautiful")

    def test_serious_themes_present(self):
        serious = neospace.get_serious_themes()
        assert len(serious) > 0
        assert "classic" in serious
        assert "corporate" in serious

    def test_beautiful_themes_present(self):
        beautiful = neospace.get_beautiful_themes()
        assert len(beautiful) > 0
        assert "neon" in beautiful
        assert "cyber" in beautiful


class TestThemeCategory:
    """Тесты get_theme_category."""

    def test_serious_theme(self):
        assert neospace.get_theme_category("classic") == "serious"
        assert neospace.get_theme_category("corporate") == "serious"

    def test_beautiful_theme(self):
        assert neospace.get_theme_category("neon") == "beautiful"
        assert neospace.get_theme_category("cyber") == "beautiful"


class TestThemeDisplayName:
    """Тесты get_theme_display_name."""

    def test_known_theme(self):
        name = neospace.get_theme_display_name("neon")
        assert "Neon" in name or "💠" in name

    def test_unknown_theme_returns_self(self):
        assert neospace.get_theme_display_name("unknown_theme") == "unknown_theme"