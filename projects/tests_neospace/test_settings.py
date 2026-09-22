"""
Тесты настроек NeoSpace OS.
"""

import os
import json
import pytest
import neospace


class TestSettingsLoad:
    """Тесты load_settings."""

    def test_returns_dict(self):
        s = neospace.load_settings()
        assert isinstance(s, dict)

    def test_has_default_keys(self):
        s = neospace.load_settings()
        for key in ("os", "hz", "browser_mode", "theme", "wallpaper"):
            assert key in s, f"Нет ключа {key}"


class TestThemeSettings:
    """Тесты get_current_theme / set_theme."""

    def test_get_current_theme(self):
        theme = neospace.get_current_theme()
        assert isinstance(theme, str)
        assert theme

    def test_set_theme(self):
        original = neospace.get_current_theme()
        try:
            neospace.set_theme("cyber")
            assert neospace.get_current_theme() == "cyber"
        finally:
            neospace.set_theme(original)


class TestWallpaperSettings:
    """Тесты get_wallpaper_path / set_wallpaper_path."""

    def test_get_wallpaper_path(self):
        path = neospace.get_wallpaper_path()
        assert isinstance(path, str)

    def test_set_wallpaper_path(self):
        original = neospace.get_wallpaper_path()
        try:
            neospace.set_wallpaper_path("C:/test/wallpaper.jpg")
            assert neospace.get_wallpaper_path() == "C:/test/wallpaper.jpg"
        finally:
            neospace.set_wallpaper_path(original)


class TestBrowserSettings:
    """Тесты get_browser_mode / set_browser_mode."""

    def test_get_browser_mode(self):
        mode = neospace.get_browser_mode()
        assert mode in ("internal", "external")

    def test_set_browser_mode(self):
        original = neospace.get_browser_mode()
        try:
            neospace.set_browser_mode("external")
            assert neospace.get_browser_mode() == "external"
        finally:
            neospace.set_browser_mode(original)