"""
Тесты геометрических и цветовых функций WhyDoes.
"""

import pytest
import whydoes


class TestHsvToHex:
    """Тесты hsv_to_hex."""

    def test_red(self):
        result = whydoes.AbstractDashboard.hsv_to_hex(0.0, 1.0, 1.0)
        assert result == "#ff0000"

    def test_green(self):
        result = whydoes.AbstractDashboard.hsv_to_hex(1/3, 1.0, 1.0)
        assert result == "#00ff00"

    def test_blue(self):
        result = whydoes.AbstractDashboard.hsv_to_hex(2/3, 1.0, 1.0)
        assert result == "#0000ff"

    def test_black(self):
        result = whydoes.AbstractDashboard.hsv_to_hex(0.0, 0.0, 0.0)
        assert result == "#000000"

    def test_white(self):
        result = whydoes.AbstractDashboard.hsv_to_hex(0.0, 0.0, 1.0)
        assert result == "#ffffff"

    def test_returns_hex_format(self):
        result = whydoes.AbstractDashboard.hsv_to_hex(0.5, 0.5, 0.5)
        assert result.startswith("#")
        assert len(result) == 7


class TestDistanceToSegment:
    """Тесты distance_to_segment."""

    def _obj(self):
        return whydoes.AbstractDashboard.__new__(whydoes.AbstractDashboard)

    def test_point_on_segment(self):
        obj = self._obj()
        d = obj.distance_to_segment(5, 0, 0, 0, 10, 0)
        assert d == 0

    def test_point_perpendicular(self):
        obj = self._obj()
        d = obj.distance_to_segment(5, 5, 0, 0, 10, 0)
        assert d == 5

    def test_point_beyond_end(self):
        obj = self._obj()
        d = obj.distance_to_segment(15, 0, 0, 0, 10, 0)
        assert d == 5

    def test_degenerate_segment(self):
        obj = self._obj()
        d = obj.distance_to_segment(8, 9, 5, 5, 5, 5)
        assert abs(d - 5.0) < 0.01