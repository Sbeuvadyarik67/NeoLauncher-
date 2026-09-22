"""
Тесты утилит get_effective_palette и build_qss.
"""

import pytest
import neobrain


# ============================================================
# get_effective_palette
# ============================================================

class TestGetEffectivePalette:
    """Тесты get_effective_palette."""

    def test_basic_palette(self):
        """Возвращает палитру из PALETTES."""
        p = neobrain.get_effective_palette("🌆 Неон", "По умолчанию")
        assert p["accent"] == neobrain.PALETTES["🌆 Неон"]["accent"]

    def test_unknown_palette_fallback(self):
        """Неизвестная тема → палитра по умолчанию (Неон)."""
        p = neobrain.get_effective_palette("НЕ СУЩЕСТВУЕТ", "По умолчанию")
        assert p["accent"] == neobrain.PALETTES["🌆 Неон"]["accent"]

    def test_terminal_style_override(self):
        """Стиль Terminal переопределяет цвета."""
        p = neobrain.get_effective_palette("🌆 Неон", "💻 Terminal")
        assert p["accent"] == "#00ff00"
        assert p["bg"] == "#0c0c0c"
        assert p["light"] is False

    def test_glass_style_override(self):
        """Стиль Glass переопределяет цвета."""
        p = neobrain.get_effective_palette("🌆 Неон", "🪟 Glass")
        assert p["bg"] == "#1a1a2e"
        assert p["text"] == "#e0e0e0"

    def test_claude_style_override(self):
        """Стиль Claude переопределяет цвета."""
        p = neobrain.get_effective_palette("🌆 Неон", "☁️ Claude")
        assert p["accent"] == "#d97757"
        assert p["light"] is True

    def test_returns_copy(self):
        """Возвращает копию, не мутирует оригинал."""
        p1 = neobrain.get_effective_palette("🌆 Неон", "По умолчанию")
        p1["accent"] = "ИЗМЕНЕНО"
        p2 = neobrain.get_effective_palette("🌆 Неон", "По умолчанию")
        assert p2["accent"] != "ИЗМЕНЕНО"


# ============================================================
# build_qss
# ============================================================

class TestBuildQss:
    """Тесты build_qss."""

    def test_returns_string(self):
        """Возвращает строку."""
        qss = neobrain.build_qss("🌆 Неон", "По умолчанию")
        assert isinstance(qss, str)
        assert len(qss) > 100

    def test_contains_main_selectors(self):
        """Содержит главные QSS-селекторы."""
        qss = neobrain.build_qss("🌆 Неон", "По умолчанию")
        assert "QMainWindow" in qss
        assert "QPushButton" in qss
        assert "QLineEdit" in qss

    def test_contains_accent_color(self):
        """Содержит акцентный цвет темы."""
        qss = neobrain.build_qss("🌆 Неон", "По умолчанию")
        accent = neobrain.PALETTES["🌆 Неон"]["accent"]
        assert accent in qss

    def test_terminal_style_green(self):
        """Terminal-стиль даёт зелёные цвета."""
        qss = neobrain.build_qss("🌆 Неон", "💻 Terminal")
        assert "#00ff00" in qss

    def test_no_unfilled_placeholders(self):
        """Не осталось незаполненных {placeholder}."""
        qss = neobrain.build_qss("🌆 Неон", "По умолчанию")
        # Проверяем, что нет одиночных "{p[" или "{{"
        assert "{p[" not in qss
        assert "{{" not in qss