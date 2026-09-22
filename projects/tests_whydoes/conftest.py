"""
Pytest — фикстуры для тестов WhyDoes.

Раз Tk работает — используем настоящий tk.Tk(), но скрытый (withdraw).
"""

import sys
import os
import tkinter as tk

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def fake_root():
    """Настоящий tk.Tk(), скрытый через withdraw."""
    root = tk.Tk()
    root.withdraw()
    yield root
    try:
        root.destroy()
    except Exception:
        pass