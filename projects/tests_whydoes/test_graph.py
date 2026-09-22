"""
Тесты логики графа WhyDoes (точки, линии, режимы).
"""

import pytest
import whydoes


class TestAddPoint:
    def test_add_point_increases_count(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        initial = len(app.points)
        app.add_point(100, 200)
        assert len(app.points) == initial + 1

    def test_added_point_has_coords(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.points.clear()
        app.selected_objects = []
        p = app.add_point(123, 456)
        assert "x" in p
        assert "y" in p


class TestLineExists:
    def test_line_exists_false(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.points.clear()
        app.lines.clear()
        p1 = app.add_point(0, 0)
        p2 = app.add_point(100, 100)
        assert app.line_exists(p1, p2) is False

    def test_line_exists_true_after_add(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.points.clear()
        app.lines.clear()
        p1 = app.add_point(0, 0)
        p2 = app.add_point(100, 100)
        app.add_line(p1, p2)
        assert app.line_exists(p1, p2) is True

    def test_line_exists_reversed(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.points.clear()
        app.lines.clear()
        p1 = app.add_point(0, 0)
        p2 = app.add_point(100, 100)
        app.add_line(p1, p2)
        assert app.line_exists(p2, p1) is True


class TestAddLine:
    def test_add_line(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.points.clear()
        app.lines.clear()
        p1 = app.add_point(0, 0)
        p2 = app.add_point(100, 100)
        app.add_line(p1, p2)
        assert len(app.lines) == 1

    def test_no_duplicate_lines(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.points.clear()
        app.lines.clear()
        p1 = app.add_point(0, 0)
        p2 = app.add_point(100, 100)
        app.add_line(p1, p2)
        app.add_line(p1, p2)
        assert len(app.lines) == 1


class TestSelectAll:
    def test_select_all(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.select_all()
        for p in app.points:
            assert p in app.selected_objects
        for l in app.lines:
            assert l in app.selected_objects


class TestDeleteSelected:
    def test_delete_selected_clears(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.select_all()
        assert len(app.selected_objects) > 0
        app.delete_selected()
        assert len(app.selected_objects) == 0
        assert len(app.points) == 0
        assert len(app.lines) == 0


class TestModes:
    def test_set_special_mode(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.set_special_mode("gravity")
        assert app.special_modes["gravity"] is True
        assert app.current_special_mode == "gravity"
        for key, val in app.special_modes.items():
            if key != "gravity":
                assert val is False

    def test_set_antistress_mode(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.set_antistress_mode("туман")
        assert app.antistress_modes["туман"] is True
        assert app.current_antistress_mode == "туман"

    def test_disable_all_modes(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.set_special_mode("gravity")
        app.disable_all_modes()
        for val in app.special_modes.values():
            assert val is False
        for val in app.antistress_modes.values():
            assert val is False
        assert app.current_special_mode is None
        assert app.current_antistress_mode is None


class TestResetCamera:
    def test_reset_camera(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.target_camera_x = 500
        app.target_camera_y = 300
        app.target_camera_zoom = 2.5
        app.reset_camera()
        assert app.target_camera_x == 0
        assert app.target_camera_y == 0
        assert app.target_camera_zoom == 1.0


class TestMovePoint:
    def test_move_point(self, fake_root):
        app = whydoes.AbstractDashboard(fake_root)
        app.points.clear()
        p = app.add_point(0, 0)
        app.camera_x = 0
        app.camera_y = 0
        app.camera_zoom = 1.0
        app.move_point(p, 200, 300)
        assert p["x"] == 200
        assert p["y"] == 300