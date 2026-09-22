"""
Тесты для launcher_settings.json — файла настроек лаунчера.
"""

import os
import json

import pytest


class TestSettingsFile:
    """Проверка launcher_settings.json."""

    def test_settings_file_exists(self, settings_path):
        """Файл launcher_settings.json существует."""
        assert os.path.exists(settings_path), \
            "launcher_settings.json не найден"

    def test_settings_is_valid_json(self, settings_path):
        """Файл — валидный JSON."""
        with open(settings_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_has_view_mode(self, settings_path):
        """Есть ключ 'view_mode'."""
        with open(settings_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "view_mode" in data, "Нет ключа 'view_mode'"

    def test_view_mode_valid(self, settings_path):
        """view_mode — 'scroll' или 'grid'."""
        with open(settings_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["view_mode"] in ("scroll", "grid"), \
            f"view_mode='{data['view_mode']}' — неверно"