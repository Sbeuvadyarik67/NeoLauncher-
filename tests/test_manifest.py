"""
Тесты для manifest.json — структура, содержимое, корректность путей.
"""

import os
import json

import pytest


# ============================================================
# СУЩЕСТВОВАНИЕ И ВАЛИДНОСТЬ
# ============================================================

class TestManifestFile:
    """Проверка файла manifest.json."""

    def test_manifest_exists(self, manifest_path):
        """Файл manifest.json существует."""
        assert os.path.exists(manifest_path), "manifest.json не найден"

    def test_manifest_is_valid_json(self, manifest_path):
        """manifest.json — валидный JSON."""
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_has_projects_key(self, manifest):
        """Есть ключ 'projects'."""
        assert "projects" in manifest, "Нет ключа 'projects'"

    def test_projects_is_dict(self, manifest):
        """'projects' — словарь."""
        assert isinstance(manifest["projects"], dict)

    def test_projects_not_empty(self, manifest):
        """'projects' не пустой."""
        assert len(manifest["projects"]) > 0, "Проектов нет"


# ============================================================
# СТРУКТУРА КАЖДОГО ПРОЕКТА
# ============================================================

class TestManifestProjects:
    """Проверка полей каждого проекта."""

    def test_each_project_has_name(self, manifest):
        """У каждого проекта есть name."""
        for pid, data in manifest["projects"].items():
            assert "name" in data, f"{pid}: нет 'name'"

    def test_each_project_has_path(self, manifest):
        """У каждого проекта есть path."""
        for pid, data in manifest["projects"].items():
            assert "path" in data, f"{pid}: нет 'path'"

    def test_each_project_has_icon(self, manifest):
        """У каждого проекта есть icon."""
        for pid, data in manifest["projects"].items():
            assert "icon" in data, f"{pid}: нет 'icon'"

    def test_each_project_has_color(self, manifest):
        """У каждого проекта есть color."""
        for pid, data in manifest["projects"].items():
            assert "color" in data, f"{pid}: нет 'color'"

    def test_each_project_has_type(self, manifest):
        """У каждого проекта есть type."""
        for pid, data in manifest["projects"].items():
            assert "type" in data, f"{pid}: нет 'type'"

    def test_types_valid(self, manifest):
        """Тип каждого проекта — валидный."""
        valid_types = {"python", "html", "exe"}
        for pid, data in manifest["projects"].items():
            assert data["type"] in valid_types, \
                f"{pid}: неверный type='{data['type']}'"

    def test_paths_exist(self, manifest, project_root):
        """Файл каждого проекта существует."""
        for pid, data in manifest["projects"].items():
            full_path = os.path.join(project_root, data["path"])
            assert os.path.exists(full_path), \
                f"{pid}: файл не найден — {full_path}"


# ============================================================
# КОНКРЕТНЫЙ ПРОЕКТ — NeoTracker
# ============================================================

class TestNeoTrackerInManifest:
    """Проверка проекта NeoTracker в манифесте."""

    def test_neotracker_present(self, manifest):
        """NeoTracker есть в manifest."""
        assert "neotracker" in manifest["projects"]

    def test_neotracker_type(self, manifest):
        """Тип NeoTracker — exe."""
        assert manifest["projects"]["neotracker"]["type"] == "exe"

    def test_neotracker_path(self, manifest):
        """Путь NeoTracker корректный."""
        path = manifest["projects"]["neotracker"]["path"]
        assert path == "projects/NeoTracker/NeoTracker.exe"

    def test_neotracker_name(self, manifest):
        """Имя NeoTracker содержит 'NeoTracker'."""
        name = manifest["projects"]["neotracker"]["name"]
        assert "NeoTracker" in name