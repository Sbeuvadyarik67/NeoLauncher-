"""
Pytest — фикстуры для тестов NeoBrain.

NeoBrain написан на PySide6, поэтому для тестов класса NeoBrainChat
нужен QApplication. Для тестов чистых функций — не нужен.
"""

import sys
import os

import pytest

# Корень проекта (папка projects/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture(scope="session")
def qapp():
    """
    Создаёт QApplication один раз на всю сессию тестов.
    Нужен для тестов, где создаются QWidget/QMainWindow.
    """
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app