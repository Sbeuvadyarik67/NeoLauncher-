"""
Тесты логики персонажа (save_character).

Требуют QApplication, потому что save_character — метод класса
NeoBrainChat, наследника QMainWindow.
"""

import pytest


class TestSaveCharacter:
    """Тесты метода save_character."""

    def _make_app(self, qapp, monkeypatch, tmp_path):
        """Создаёт экземпляр NeoBrainChat с изолированными настройками."""
        import neobrain

        def patched_load(self):
            return {
                "ollama_url": "http://localhost:11434", "model": "llama3.2:3b",
                "temperature": 0.7, "theme": "🌆 Неон", "style": "По умолчанию",
                "current_character": None, "characters": {}, "history": [],
                "auto_save": True, "stream_mode": True, "max_tokens": 512, "lang": "ru"
            }

        monkeypatch.setattr(neobrain.NeoBrainChat, "load_settings", patched_load)
        monkeypatch.setattr(neobrain.NeoBrainChat, "save_settings", lambda self: None)
        monkeypatch.setattr(neobrain.NeoBrainChat, "save_history", lambda self: None)
        monkeypatch.setattr(neobrain.NeoBrainChat, "add_system_message",
                            lambda self, s, t: None)

        app = neobrain.NeoBrainChat()
        return app

    def test_male_prompt(self, qapp, monkeypatch, tmp_path):
        """Мужской персонаж получает правильный промпт."""
        app = self._make_app(qapp, monkeypatch, tmp_path)

        class FakeEntry:
            def __init__(self, text=""): self._text = text
            def text(self): return self._text
        class FakeText:
            def __init__(self, text=""): self._text = text
            def toPlainText(self): return self._text
        class FakeGroup:
            def checkedId(self): return 0
        class FakeDialog:
            def accept(self): pass

        app.save_character(
            FakeEntry("Алекс"),
            FakeGroup(),
            FakeEntry("спокойный"),
            FakeText("добрый"),
            FakeDialog(),
        )

        char = app.current_character
        assert char is not None
        assert char["name"] == "Алекс"
        assert char["gender"] == "мужской"
        assert char["pronoun"] == "он"
        assert "я сделал" in char["prompt"]

    def test_female_prompt(self, qapp, monkeypatch, tmp_path):
        """Женский персонаж получает правильный промпт."""
        app = self._make_app(qapp, monkeypatch, tmp_path)

        class FakeEntry:
            def __init__(self, text=""): self._text = text
            def text(self): return self._text
        class FakeText:
            def __init__(self, text=""): self._text = text
            def toPlainText(self): return self._text
        class FakeGroup:
            def checkedId(self): return 1
        class FakeDialog:
            def accept(self): pass

        app.save_character(
            FakeEntry("Анна"),
            FakeGroup(),
            FakeEntry("нежная"),
            FakeText("заботливая"),
            FakeDialog(),
        )

        char = app.current_character
        assert char["name"] == "Анна"
        assert char["gender"] == "женский"
        assert char["pronoun"] == "она"
        assert "я сделала" in char["prompt"]

    def test_empty_name_rejected(self, qapp, monkeypatch, tmp_path):
        """Пустое имя — персонаж не создаётся."""
        app = self._make_app(qapp, monkeypatch, tmp_path)

        from PySide6.QtWidgets import QMessageBox
        monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)

        class FakeEntry:
            def __init__(self, text=""): self._text = text
            def text(self): return self._text
        class FakeText:
            def __init__(self, text=""): self._text = text
            def toPlainText(self): return self._text
        class FakeGroup:
            def checkedId(self): return 0
        class FakeDialog:
            def accept(self): pass

        app.save_character(
            FakeEntry(""),
            FakeGroup(),
            FakeEntry(""),
            FakeText(""),
            FakeDialog(),
        )

        assert app.current_character is None

    def test_character_saved_to_settings(self, qapp, monkeypatch, tmp_path):
        """Персонаж сохраняется в settings.characters."""
        app = self._make_app(qapp, monkeypatch, tmp_path)

        class FakeEntry:
            def __init__(self, text=""): self._text = text
            def text(self): return self._text
        class FakeText:
            def __init__(self, text=""): self._text = text
            def toPlainText(self): return self._text
        class FakeGroup:
            def checkedId(self): return 0
        class FakeDialog:
            def accept(self): pass

        app.save_character(
            FakeEntry("Борис"),
            FakeGroup(),
            FakeEntry("строгий"),
            FakeText(""),
            FakeDialog(),
        )

        assert "Борис" in app.settings["characters"]
        assert app.settings["characters"]["Борис"]["name"] == "Борис"