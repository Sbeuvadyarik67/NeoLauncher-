"""
Тесты файловых операций NeoSpace OS.
"""

import os
import pytest
import neospace


class TestGetFileSize:
    """Тесты get_file_size."""

    def test_file_size(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"x" * 1000)
        assert neospace.get_file_size(str(f)) == 1000

    def test_folder_size(self, tmp_path):
        folder = tmp_path / "folder"
        folder.mkdir()
        (folder / "a.txt").write_bytes(b"x" * 500)
        (folder / "b.txt").write_bytes(b"y" * 300)
        assert neospace.get_file_size(str(folder)) == 800

    def test_empty_folder(self, tmp_path):
        folder = tmp_path / "empty"
        folder.mkdir()
        assert neospace.get_file_size(str(folder)) == 0


class TestCopyWithProgress:
    """Тесты copy_with_progress."""

    def test_copy_file(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_bytes(b"x" * 5000)
        dst = tmp_path / "dst.txt"

        neospace.copy_with_progress(str(src), str(dst))

        assert dst.exists()
        assert dst.stat().st_size == 5000

    def test_progress_callback(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_bytes(b"x" * 20000)
        dst = tmp_path / "dst.txt"

        calls = []
        def callback(current, total):
            calls.append((current, total))

        neospace.copy_with_progress(str(src), str(dst), callback)

        assert len(calls) > 0
        assert calls[-1][0] == 20000