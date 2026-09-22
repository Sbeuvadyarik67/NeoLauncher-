"""
Pytest — общие фикстуры для тестов NeoLauncher.
"""

import sys
import os
import json

import pytest

# Корень проекта — папка NeoLauncher_АКТУАЛОЧКА
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def project_root():
    """Путь к корню проекта."""
    return PROJECT_ROOT


@pytest.fixture
def manifest_path(project_root):
    """Путь к manifest.json."""
    return os.path.join(project_root, "manifest.json")


@pytest.fixture
def manifest(manifest_path):
    """Загруженный manifest.json."""
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def settings_path(project_root):
    """Путь к launcher_settings.json."""
    return os.path.join(project_root, "launcher_settings.json")