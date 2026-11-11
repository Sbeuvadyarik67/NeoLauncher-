import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Добавляем корень проекта в path, чтобы pytest мог найти launcher.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from launcher import NeoLauncher


@pytest.fixture
def app(tmp_path):
    """
    Фикстура: создает экземпляр NeoLauncher без открытия GUI.
    tmp_path - это встроенная в pytest временная папка, она удалится сама после теста.
    """
    with patch("launcher.tk.Tk"), patch("launcher.NeoLauncher.setup_ui"), patch(
        "launcher.NeoLauncher._apply_theme"
    ), patch("launcher.NeoLauncher.render_projects"):

        instance = NeoLauncher.__new__(NeoLauncher)
        instance.root = MagicMock()
        instance.base_dir = str(tmp_path)
        instance.manifest_path = str(tmp_path / "manifest.json")
        instance.settings_path = str(tmp_path / "launcher_settings.json")
        instance.theme_name = "neon"
        instance.settings = {"theme": "neon"}
        instance.manifest = {"projects": {}}
        instance._cards = []
        instance._grid_frame = None
        instance._resize_job = None
        instance._entry_anim_jobs = []
        instance.status_label = MagicMock()

        yield instance


# ============================================================
# ТЕСТЫ ЗАГРУЗКИ И СОХРАНЕНИЯ ДАННЫХ
# ============================================================


def test_load_manifest_missing(app):
    manifest = app.load_manifest()
    assert manifest == {"projects": {}}


def test_load_manifest_valid(app, tmp_path):
    data = {"projects": {"test_proj": {"name": "TestProject"}}}
    Path(app.manifest_path).write_text(json.dumps(data), encoding="utf-8")

    manifest = app.load_manifest()
    assert manifest["projects"]["test_proj"]["name"] == "TestProject"


def test_load_settings_adds_missing_keys(app, tmp_path):
    """Проверяем, что load_settings добавляет отсутствующие ключи из default."""
    # Сохраняем файл только с одним ключом, хотя в будущем их может быть больше
    Path(app.settings_path).write_text('{"custom_key": "value"}', encoding="utf-8")

    settings = app.load_settings()
    assert settings["custom_key"] == "value"
    assert settings["theme"] == "neon"  # Дефолтный ключ должен добавиться


def test_load_settings_corrupted(app, tmp_path):
    Path(app.settings_path).write_text("это не json {", encoding="utf-8")
    settings = app.load_settings()
    assert settings == {"theme": "neon"}


def test_save_and_load_settings_roundtrip(app):
    app.settings["theme"] = "claude"
    app.save_settings()

    assert os.path.exists(app.settings_path)
    loaded = app.load_settings()
    assert loaded["theme"] == "claude"


# ============================================================
# ТЕСТЫ ЗАПУСКА ПРОЕКТОВ
# ============================================================


def test_launch_project_not_found(app):
    with patch("launcher.messagebox") as mock_msg:
        app.manifest = {"projects": {}}
        app.launch_project("ghost_project")
        mock_msg.showerror.assert_called_once()


def test_launch_project_path_missing(app):
    app.manifest = {"projects": {"p1": {"name": "P1", "path": "missing_file.exe"}}}
    with patch("launcher.messagebox") as mock_msg:
        app.launch_project("p1")
        mock_msg.showerror.assert_called_once()


def test_launch_python_project(app, tmp_path):
    fake_script = tmp_path / "script.py"
    fake_script.write_text("print('hello')")

    app.manifest = {
        "projects": {
            "py_proj": {"name": "PyProj", "path": "script.py", "type": "python"}
        }
    }

    with patch("launcher.subprocess.Popen") as mock_popen, patch(
        "launcher.shutil.which", return_value="python"
    ):

        app.launch_project("py_proj")
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert "python" in call_args
        assert call_args[-1].endswith("script.py")


def test_launch_html_project(app, tmp_path):
    fake_html = tmp_path / "index.html"
    fake_html.write_text("<h1>Hi</h1>")

    app.manifest = {
        "projects": {
            "web_proj": {"name": "WebProj", "path": "index.html", "type": "html"}
        }
    }

    with patch("webbrowser.open") as mock_web:
        app.launch_project("web_proj")
        mock_web.assert_called_once()


def test_launch_neospace_project(app, tmp_path):
    """Специальный тест для neospace, который использует os.startfile."""
    fake_exe = tmp_path / "neospace.exe"
    fake_exe.write_text("fake exe")

    app.manifest = {
        "projects": {"neospace": {"name": "NeoSpace", "path": "neospace.exe"}}
    }

    with patch("os.startfile") as mock_startfile:
        app.launch_project("neospace")
        mock_startfile.assert_called_once()
        assert mock_startfile.call_args[0][0].endswith("neospace.exe")


def test_launch_unknown_type_project(app, tmp_path):
    """Fallback: если тип не указан, запускаем как обычный файл через subprocess."""
    fake_file = tmp_path / "document.pdf"
    fake_file.write_text("fake pdf")

    app.manifest = {
        "projects": {
            "pdf_proj": {"name": "Doc", "path": "document.pdf"}  # type не указан
        }
    }

    with patch("launcher.subprocess.Popen") as mock_popen:
        app.launch_project("pdf_proj")
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert call_args[0].endswith("document.pdf")


# ============================================================
# ТЕСТЫ UI ЛОГИКИ И УТИЛИТ
# ============================================================


def test_toggle_theme(app):
    assert app.theme_name == "neon"
    app.toggle_theme()
    assert app.theme_name == "claude"
    assert app.settings["theme"] == "claude"
    app.toggle_theme()
    assert app.theme_name == "neon"


def test_mute_for_claude(app):
    """Проверяем, что яркий цвет корректно приглушается."""
    bright_pink = "#FF007F"
    muted = app._mute_for_claude(bright_pink)

    # Результат должен оставаться валидным HEX-цветом
    assert muted.startswith("#")
    assert len(muted) == 7

    # Он должен быть темнее и менее насыщенным, чем оригинал
    # (просто проверяем, что функция не упала и вернула строку)
    assert muted != bright_pink


def test_mute_for_claude_invalid_input(app):
    """Если передан невалидный цвет, функция должна вернуть его как есть."""
    invalid_color = "not-a-color"
    assert app._mute_for_claude(invalid_color) == invalid_color
