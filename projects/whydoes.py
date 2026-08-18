import tkinter as tk
from tkinter import Canvas, Frame, Label, Button, filedialog, messagebox
import math
import random
import time
import colorsys
import json
import os
from datetime import datetime

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False


class AbstractDashboard:
    def __init__(self, root):
        self.root = root
        self.width = 1360
        self.height = 768
        self.is_fullscreen = False
        
        self.target_fps = 60
        self.frame_time = 1.0 / self.target_fps
        self.last_time = time.time()
        self.delta_time = 0.0
        self.fps_counter = 0
        self.fps_display = 0
        self.fps_timer = 0.0

        self.bg_color = "#0f1115"
        self.panel_bg = "#161b22"
        self.text_color = "#8b9bb4"
        self.accent = "#58a6ff"

        self.root.title("🌀 Бесконечное безумие v5.0")
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.configure(bg=self.bg_color)

        # Горячие клавиши
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<f>", lambda e: self.activate_mode("fractal"))
        self.root.bind("<s>", lambda e: self.save_scene())
        self.root.bind("<l>", lambda e: self.load_scene())
        self.root.bind("<p>", lambda e: self.export_png())
        self.root.bind("<b>", lambda e: self.activate_mode("brush"))
        self.root.bind("<d>", lambda e: self.activate_mode("rain"))
        self.root.bind("<u>", lambda e: self.activate_mode("universe"))
        self.root.bind("<c>", lambda e: self.clear_all())
        self.root.bind("<r>", lambda e: self.random_generate())
        self.root.bind("<space>", self.toggle_special_mode)
        
        # НОВАЯ КЛАВИША АВАРИЙНОГО СБРОСА
        self.root.bind("<x>", lambda e: self.emergency_reset())
        self.root.bind("<X>", lambda e: self.emergency_reset())
        
        # Камера
        self.camera_x = 0
        self.camera_y = 0
        self.camera_zoom = 1.0
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.camera_drag_start_x = 0
        self.camera_drag_start_y = 0
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.target_camera_zoom = 1.0
        self.camera_smoothness = 0.15

        # Режимы (сокращённые до 12)
        self.special_modes = {
            "gravity": False,
            "music": False,
            "evolution": False,
            "black_hole": False,
            "tornado": False,
            "dna_spiral": False,
            "fractal": False,
            "brush": False,
            "rain": False,
            "universe": False,
            "kaleidoscope": False,
            "explosion": False
        }
        self.current_special_mode = None
        self.gravity_force = 0.01
        self.music_beat = 0
        self.evolution_counter = 0
        self.destroy_particles = []
        self.neural_signals = []
        self.black_hole_pos = (self.width/2, self.height/2)
        self.black_hole_strength = 0.5
        self.tornado_center = (self.width/2, self.height/2)
        self.tornado_radius = 200
        self.dna_angle = 0
        
        # Для кисти
        self.brush_active = False
        self.brush_size = 10
        self.brush_color = "#ff2d8a"
        
        # Для дождя
        self.rain_drops = []
        
        # Для вселенной
        self.universe_particles = []

        # Точки и линии
        self.points = []
        self.lines = []
        self.selected_objects = []
        self.hovered_object = None
        self.interactive_mode = "select"
        self.temp_point = None
        self.point_count = 20
        self.line_count = 0

        # Основной контейнер
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель
        self.left_panel = Frame(self.main_frame, width=280, bg=self.panel_bg)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH)
        self.left_panel.pack_propagate(False)

        self.drag_bar = Frame(self.left_panel, width=8, bg="#21262d", cursor="fleur")
        self.drag_bar.pack(side=tk.LEFT, fill=tk.BOTH)
        self._make_draggable(self.drag_bar)

        self.setup_left_panel()

        # Холст
        self.canvas = Canvas(self.main_frame, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<ButtonPress-3>", self.on_right_click)
        self.canvas.bind("<MouseWheel>", self.zoom_camera)
        self.canvas.bind("<Motion>", self.on_mouse_hover)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.root.bind("<Control-0>", self.reset_camera)
        self.root.bind("<Delete>", self.delete_selected)
        self.root.bind("<Control-a>", self.select_all)

        # Параметры
        self.particles = []
        self.particle_count = 40
        self.time_offset = 0.0
        self.stars = []
        self.star_count = 30

        self.init_particles()
        self.init_stars()
        self.init_random_points_and_lines()
        self.animate()

    # --- НОВЫЙ МЕТОД: АВАРИЙНЫЙ СБРОС ---
    def emergency_reset(self):
        """АВАРИЙНЫЙ СБРОС — очищает всё мгновенно"""
        self.points.clear()
        self.lines.clear()
        self.selected_objects.clear()
        self.destroy_particles.clear()
        self.rain_drops.clear()
        self.universe_particles.clear()
        self.neural_signals = []
        self.temp_point = None
        self.brush_active = False
        
        # Сбрасываем все режимы
        for key in self.special_modes:
            self.special_modes[key] = False
        self.current_special_mode = None
        
        # Сбрасываем камеру
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.target_camera_zoom = 1.0
        
        self.status_label.config(text="💥 АВАРИЙНЫЙ СБРОС ВЫПОЛНЕН! (X)")
        self.create_sound_effect()
    
    def create_sound_effect(self):
        if SOUND_AVAILABLE:
            try:
                winsound.Beep(random.randint(400, 800), 50)
            except:
                pass

    # --- БАЗОВЫЕ МЕТОДЫ ---
    def _make_draggable(self, widget):
        widget.bind("<ButtonPress-1>", self.start_drag)
        widget.bind("<B1-Motion>", self.do_drag)

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def do_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    @staticmethod
    def hsv_to_hex(h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    # --- УПРАВЛЕНИЕ РЕЖИМАМИ ---
    def activate_mode(self, mode_name):
        for key in self.special_modes:
            self.special_modes[key] = False
        if mode_name in self.special_modes:
            self.special_modes[mode_name] = True
            self.current_special_mode = mode_name
            self.status_label.config(text=f"🌀 Режим: {mode_name.upper()}")
            if mode_name == "fractal":
                self.generate_fractal(self.width/2, self.height/2, 150, 5, 0)
            elif mode_name == "brush":
                self.brush_active = True
            elif mode_name == "rain":
                self.init_rain()
            elif mode_name == "universe":
                self.init_universe()
            elif mode_name == "kaleidoscope":
                self.generate_kaleidoscope()
            elif mode_name == "explosion":
                self.create_explosion()

    def toggle_special_mode(self, event=None):
        modes = list(self.special_modes.keys())
        if self.current_special_mode is None:
            self.current_special_mode = 0
        else:
            self.current_special_mode = (self.current_special_mode + 1) % len(modes)
        for key in self.special_modes:
            self.special_modes[key] = False
        if self.current_special_mode is not None:
            mode_name = modes[self.current_special_mode]
            self.special_modes[mode_name] = True
            self.status_label.config(text=f"🧠 Режим: {mode_name.upper()}")
            if mode_name == "fractal":
                self.generate_fractal(self.width/2, self.height/2, 150, 5, 0)
            elif mode_name == "brush":
                self.brush_active = True
            elif mode_name == "rain":
                self.init_rain()
            elif mode_name == "universe":
                self.init_universe()
            elif mode_name == "kaleidoscope":
                self.generate_kaleidoscope()
            elif mode_name == "explosion":
                self.create_explosion()

    # --- ГЕНЕРАЦИЯ ---
    def generate_fractal(self, x, y, size, depth, angle):
        if depth == 0 or size < 2:
            color = self.hsv_to_hex((angle / (2 * math.pi)) % 1.0, 0.8, 0.6)
            self.points.append({
                "x": x, "y": y,
                "color": color,
                "size": random.uniform(3, 6),
                "selected": False,
                "id": len(self.points),
                "pulse_offset": random.uniform(0, 2 * math.pi),
                "vx": random.uniform(-0.1, 0.1),
                "vy": random.uniform(-0.1, 0.1)
            })
            return
        branches = random.randint(2, 3)
        for i in range(branches):
            new_angle = angle + random.uniform(-0.8, 0.8) + (i - branches/2) * 0.5
            new_size = size * random.uniform(0.4, 0.7)
            new_x = x + size * math.cos(new_angle) * 0.8
            new_y = y + size * math.sin(new_angle) * 0.8
            if len(self.points) > 0:
                parent = self.points[-1]
                self.add_line(parent, {
                    "x": new_x, "y": new_y,
                    "color": self.hsv_to_hex((new_angle / (2 * math.pi)) % 1.0, 0.6, 0.5)
                })
            self.generate_fractal(new_x, new_y, new_size, depth - 1, new_angle)

    def generate_kaleidoscope(self):
        center_x, center_y = self.width/2, self.height/2
        for i in range(40):
            angle = i * 2 * math.pi / 40
            radius = random.uniform(50, 180)
            for j in range(6):
                mirror_angle = angle + j * math.pi / 3
                x = center_x + radius * math.cos(mirror_angle)
                y = center_y + radius * math.sin(mirror_angle)
                color = self.hsv_to_hex((i / 40 + j / 6) % 1.0, 0.8, 0.6)
                self.points.append({
                    "x": x, "y": y,
                    "color": color,
                    "size": random.uniform(3, 5),
                    "selected": False,
                    "id": len(self.points),
                    "pulse_offset": random.uniform(0, 2 * math.pi),
                    "vx": random.uniform(-0.1, 0.1),
                    "vy": random.uniform(-0.1, 0.1)
                })

    def create_explosion(self):
        center_x, center_y = self.width/2, self.height/2
        for _ in range(80):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(10, 80)
            x = center_x + distance * math.cos(angle)
            y = center_y + distance * math.sin(angle)
            color = self.hsv_to_hex(random.uniform(0, 1), 0.9, 0.7)
            self.points.append({
                "x": x, "y": y,
                "color": color,
                "size": random.uniform(2, 6),
                "selected": False,
                "id": len(self.points),
                "pulse_offset": random.uniform(0, 2 * math.pi),
                "vx": random.uniform(-1, 1),
                "vy": random.uniform(-1, 1)
            })

    def init_rain(self):
        self.rain_drops = []
        for _ in range(30):
            self.rain_drops.append({
                "x": random.randint(0, self.width),
                "y": random.randint(-self.height, 0),
                "speed": random.uniform(3, 6),
                "size": random.uniform(2, 4),
                "color": self.hsv_to_hex(random.uniform(0, 1), 0.8, 0.6),
                "trail": []
            })

    def init_universe(self):
        self.universe_particles = []
        for _ in range(60):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.universe_particles.append({
                "x": self.width/2, "y": self.height/2,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": random.uniform(2, 4),
                "color": self.hsv_to_hex(random.uniform(0, 1), 0.8, 0.6),
                "life": 1.0
            })

    def init_random_points_and_lines(self):
        for _ in range(self.point_count):
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            color = random.choice(["#58a6ff", "#8b5cf6", "#2ea043", "#ff7b72", "#f0c674"])
            size = random.uniform(4, 7)
            self.points.append({
                "x": x, "y": y,
                "color": color,
                "size": size,
                "selected": False,
                "id": len(self.points),
                "pulse_offset": random.uniform(0, 2 * math.pi),
                "vx": random.uniform(-0.2, 0.2),
                "vy": random.uniform(-0.2, 0.2)
            })
        for _ in range(12):
            if len(self.points) >= 2:
                p1 = random.choice(self.points)
                p2 = random.choice(self.points)
                if p1 != p2 and not self.line_exists(p1, p2):
                    color = random.choice(["#58a6ff", "#8b5cf6", "#ff7b72", "#2ea043"])
                    self.lines.append({
                        "point1": p1,
                        "point2": p2,
                        "color": color,
                        "width": random.uniform(1, 2),
                        "selected": False
                    })
        self.line_count = len(self.lines)

    # --- РАБОТА С ЛИНИЯМИ ---
    def line_exists(self, p1, p2):
        for line in self.lines:
            if (line["point1"] == p1 and line["point2"] == p2) or \
               (line["point1"] == p2 and line["point2"] == p1):
                return True
        return False

    def add_line(self, point1, point2):
        if point1 and point2 and point1 != point2 and not self.line_exists(point1, point2):
            color = random.choice(["#58a6ff", "#8b5cf6", "#ff7b72", "#2ea043"])
            self.lines.append({
                "point1": point1,
                "point2": point2,
                "color": color,
                "width": random.uniform(1, 2),
                "selected": False
            })
            self.line_count += 1

    def add_point(self, x, y):
        world_x = x / self.camera_zoom - self.camera_x
        world_y = y / self.camera_zoom - self.camera_y
        color = self.brush_color if self.special_modes.get("brush") else random.choice(["#58a6ff", "#8b5cf6", "#2ea043", "#ff7b72"])
        point = {
            "x": world_x, "y": world_y,
            "color": color,
            "size": self.brush_size if self.special_modes.get("brush") else random.uniform(4, 7),
            "selected": False,
            "id": len(self.points),
            "pulse_offset": random.uniform(0, 2 * math.pi),
            "vx": random.uniform(-0.1, 0.1),
            "vy": random.uniform(-0.1, 0.1)
        }
        self.points.append(point)
        return point

    # --- ПРИМЕНЕНИЕ ЭФФЕКТОВ ---
    def apply_special_effects(self):
        if self.special_modes.get("gravity", False):
            for i, p1 in enumerate(self.points):
                for j, p2 in enumerate(self.points):
                    if i >= j: continue
                    dx = p2["x"] - p1["x"]
                    dy = p2["y"] - p1["y"]
                    dist = math.hypot(dx, dy)
                    if dist < 300 and dist > 10:
                        force = self.gravity_force / (dist + 1)
                        p1["vx"] += dx * force * 0.05
                        p1["vy"] += dy * force * 0.05
                        p2["vx"] -= dx * force * 0.05
                        p2["vy"] -= dy * force * 0.05

        if self.special_modes.get("music", False):
            self.music_beat += self.delta_time * 2
            beat = math.sin(self.music_beat) * 0.5 + 0.5
            for i, point in enumerate(self.points):
                point["size"] = 5 + 5 * (0.5 + 0.5 * math.sin(self.music_beat + i * 0.5))
                h = (i / max(1, len(self.points)) + beat * 0.2) % 1.0
                point["color"] = self.hsv_to_hex(h, 0.8, 0.6)

        if self.special_modes.get("evolution", False):
            self.evolution_counter += self.delta_time
            if self.evolution_counter > 2.0 and len(self.points) < 60:
                self.evolution_counter = 0
                if self.points:
                    parent = random.choice(self.points)
                    new_x = parent["x"] + random.uniform(-40, 40)
                    new_y = parent["y"] + random.uniform(-40, 40)
                    color = self.hsv_to_hex(random.uniform(0, 1), 0.8, 0.6)
                    self.points.append({
                        "x": new_x, "y": new_y,
                        "color": color,
                        "size": random.uniform(4, 6),
                        "selected": False,
                        "id": len(self.points),
                        "pulse_offset": random.uniform(0, 2 * math.pi),
                        "vx": random.uniform(-0.3, 0.3),
                        "vy": random.uniform(-0.3, 0.3)
                    })
                    self.add_line(parent, self.points[-1])

        if self.special_modes.get("black_hole", False):
            bh_x, bh_y = self.black_hole_pos
            for point in self.points:
                dx = bh_x - point["x"]
                dy = bh_y - point["y"]
                dist = math.hypot(dx, dy)
                if dist > 10:
                    force = self.black_hole_strength / (dist * 0.5 + 1)
                    point["vx"] += dx * force * 0.03
                    point["vy"] += dy * force * 0.03
                    if dist < 15:
                        self.destroy_point(point)
            self.black_hole_pos = (self.width/2 + 30 * math.sin(self.time_offset * 0.3),
                                   self.height/2 + 30 * math.cos(self.time_offset * 0.5))

        if self.special_modes.get("tornado", False):
            tx, ty = self.tornado_center
            for point in self.points:
                dx = point["x"] - tx
                dy = point["y"] - ty
                dist = math.hypot(dx, dy)
                if dist < self.tornado_radius:
                    angle = math.atan2(dy, dx) + self.time_offset * 0.5
                    force = (1 - dist / self.tornado_radius) * 0.08
                    point["vx"] += math.cos(angle + math.pi/2) * force * 2
                    point["vy"] += math.sin(angle + math.pi/2) * force * 2
                    point["vy"] -= 0.03 * (1 - dist / self.tornado_radius)

        if self.special_modes.get("dna_spiral", False):
            self.dna_angle += self.delta_time * 0.5
            for i, point in enumerate(self.points):
                t = i / max(1, len(self.points))
                angle = self.dna_angle + t * 4 * math.pi
                radius = 100 + 30 * math.sin(t * 8 + self.time_offset)
                target_x = self.width/2 + radius * math.cos(angle)
                target_y = self.height/2 + (t - 0.5) * 300
                point["x"] += (target_x - point["x"]) * 0.015
                point["y"] += (target_y - point["y"]) * 0.015

        if self.special_modes.get("rain", False):
            for drop in self.rain_drops:
                drop["y"] += drop["speed"]
                if drop["y"] > self.height:
                    drop["y"] = -10
                    drop["x"] = random.randint(0, self.width)
                    drop["color"] = self.hsv_to_hex(random.uniform(0, 1), 0.8, 0.6)

        if self.special_modes.get("universe", False):
            for particle in self.universe_particles:
                particle["x"] += particle["vx"]
                particle["y"] += particle["vy"]
                particle["life"] -= 0.003
                if particle["life"] > 0 and random.random() < 0.2:
                    self.points.append({
                        "x": particle["x"], "y": particle["y"],
                        "color": particle["color"],
                        "size": particle["size"] * particle["life"],
                        "selected": False,
                        "id": len(self.points),
                        "pulse_offset": random.uniform(0, 2 * math.pi),
                        "vx": 0, "vy": 0
                    })
                if particle["life"] <= 0:
                    particle["life"] = 1.0
                    particle["x"] = self.width/2
                    particle["y"] = self.height/2
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2, 6)
                    particle["vx"] = math.cos(angle) * speed
                    particle["vy"] = math.sin(angle) * speed
                    particle["color"] = self.hsv_to_hex(random.uniform(0, 1), 0.8, 0.6)

        if self.special_modes.get("kaleidoscope", False):
            center_x, center_y = self.width/2, self.height/2
            for point in self.points:
                dx = point["x"] - center_x
                dy = point["y"] - center_y
                angle = math.atan2(dy, dx) + self.time_offset * 0.2
                dist = math.hypot(dx, dy)
                new_x = center_x + dist * math.cos(angle)
                new_y = center_y + dist * math.sin(angle)
                point["x"] += (new_x - point["x"]) * 0.015
                point["y"] += (new_y - point["y"]) * 0.015

        if self.special_modes.get("explosion", False):
            for point in self.points:
                point["vx"] *= 0.98
                point["vy"] *= 0.98
                point["x"] += point["vx"]
                point["y"] += point["vy"]

    def destroy_point(self, point):
        if point in self.points:
            for _ in range(15):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                self.destroy_particles.append({
                    "x": point["x"], "y": point["y"],
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "size": random.uniform(2, 4),
                    "color": point["color"],
                    "life": random.uniform(0.5, 1.5),
                    "max_life": random.uniform(0.5, 1.5)
                })
            self.delete_object(point, "point")

    # --- ОБРАБОТЧИКИ ---
    def get_object_at(self, x, y):
        world_x = x / self.camera_zoom - self.camera_x
        world_y = y / self.camera_zoom - self.camera_y
        for point in self.points:
            if math.hypot(point["x"] - world_x, point["y"] - world_y) < point["size"] * 2:
                return point, "point"
        for line in self.lines:
            p1, p2 = line["point1"], line["point2"]
            dist = self.distance_to_segment(world_x, world_y, p1["x"], p1["y"], p2["x"], p2["y"])
            if dist < 10 / self.camera_zoom:
                return line, "line"
        return None, None

    def distance_to_segment(self, px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)))
        return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))

    def delete_object(self, obj, obj_type):
        if obj_type == "point":
            self.lines = [l for l in self.lines if l["point1"] != obj and l["point2"] != obj]
            if obj in self.points:
                self.points.remove(obj)
            if obj in self.selected_objects:
                self.selected_objects.remove(obj)
        elif obj_type == "line":
            if obj in self.lines:
                self.lines.remove(obj)
            if obj in self.selected_objects:
                self.selected_objects.remove(obj)

    def delete_selected(self, event=None):
        to_delete = []
        for obj in self.selected_objects:
            if obj in self.points:
                self.lines = [l for l in self.lines if l["point1"] != obj and l["point2"] != obj]
                to_delete.append(obj)
            elif obj in self.lines:
                to_delete.append(obj)
        for obj in to_delete:
            if obj in self.points:
                self.points.remove(obj)
            elif obj in self.lines:
                self.lines.remove(obj)
        self.selected_objects = []

    def select_all(self, event=None):
        self.selected_objects = self.points.copy() + self.lines.copy()
        for obj in self.selected_objects:
            if "selected" in obj:
                obj["selected"] = True

    def move_point(self, point, new_x, new_y):
        point["x"] = new_x / self.camera_zoom - self.camera_x
        point["y"] = new_y / self.camera_zoom - self.camera_y

    def split_line(self, line, new_point):
        if line in self.lines:
            p1, p2 = line["point1"], line["point2"]
            self.lines.remove(line)
            self.add_line(p1, new_point)
            self.add_line(new_point, p2)
            self.points.append(new_point)

    def clear_all(self):
        if messagebox.askyesno("Очистка", "Удалить всё?"):
            self.points.clear()
            self.lines.clear()
            self.selected_objects.clear()
            self.destroy_particles.clear()
            self.status_label.config(text="🧹 Очищено!")

    def random_generate(self):
        self.clear_all()
        self.init_random_points_and_lines()
        self.status_label.config(text=f"🎲 Сгенерировано: {len(self.points)} точек, {len(self.lines)} линий")

    def save_scene(self):
        try:
            data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "points": [{"x": p["x"], "y": p["y"], "color": p["color"], "size": p["size"]} for p in self.points],
                "lines": [{"p1": {"x": l["point1"]["x"], "y": l["point1"]["y"]},
                          "p2": {"x": l["point2"]["x"], "y": l["point2"]["y"]},
                          "color": l["color"]} for l in self.lines]
            }
            filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.status_label.config(text=f"✅ Сохранено: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def load_scene(self):
        try:
            filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.points.clear()
                self.lines.clear()
                self.selected_objects.clear()
                point_map = {}
                for p_data in data.get("points", []):
                    point = {
                        "x": p_data["x"], "y": p_data["y"],
                        "color": p_data.get("color", "#58a6ff"),
                        "size": p_data.get("size", random.uniform(4, 7)),
                        "selected": False,
                        "id": len(self.points),
                        "pulse_offset": random.uniform(0, 2 * math.pi),
                        "vx": random.uniform(-0.1, 0.1),
                        "vy": random.uniform(-0.1, 0.1)
                    }
                    self.points.append(point)
                    point_map[(p_data["x"], p_data["y"])] = point
                for l_data in data.get("lines", []):
                    p1_key = (l_data["p1"]["x"], l_data["p1"]["y"])
                    p2_key = (l_data["p2"]["x"], l_data["p2"]["y"])
                    if p1_key in point_map and p2_key in point_map:
                        self.add_line(point_map[p1_key], point_map[p2_key])
                self.status_label.config(text=f"✅ Загружено: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def export_png(self):
        if not PIL_AVAILABLE:
            messagebox.showerror("Ошибка", "Установите Pillow: pip install Pillow")
            return
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if filename:
                img = Image.new("RGB", (self.width, self.height), self.bg_color)
                draw = ImageDraw.Draw(img)
                for point in self.points:
                    x = int((point["x"] + self.camera_x) * self.camera_zoom + self.width/2)
                    y = int((point["y"] + self.camera_y) * self.camera_zoom + self.height/2)
                    size = int(point["size"] * self.camera_zoom)
                    draw.ellipse([x-size, y-size, x+size, y+size], fill=point["color"].lstrip('#'))
                for line in self.lines:
                    p1, p2 = line["point1"], line["point2"]
                    x1 = int((p1["x"] + self.camera_x) * self.camera_zoom + self.width/2)
                    y1 = int((p1["y"] + self.camera_y) * self.camera_zoom + self.height/2)
                    x2 = int((p2["x"] + self.camera_x) * self.camera_zoom + self.width/2)
                    y2 = int((p2["y"] + self.camera_y) * self.camera_zoom + self.height/2)
                    draw.line([x1, y1, x2, y2], fill=line["color"].lstrip('#'), width=int(line["width"] * 2))
                img.save(filename)
                self.status_label.config(text=f"✅ PNG: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # --- СОБЫТИЯ МЫШИ ---
    def on_mouse_down(self, event):
        obj, obj_type = self.get_object_at(event.x, event.y)
        if self.special_modes.get("brush", False):
            self.add_point(event.x, event.y)
            return
        if self.interactive_mode == "select":
            if obj:
                if event.state & 0x0004:
                    if obj in self.selected_objects:
                        self.selected_objects.remove(obj)
                        obj["selected"] = False
                    else:
                        self.selected_objects.append(obj)
                        obj["selected"] = True
                else:
                    self.selected_objects = [obj] if obj else []
                    for o in self.points + self.lines:
                        o["selected"] = o in self.selected_objects
                self.dragging = False
            else:
                self.selected_objects = []
                for o in self.points + self.lines:
                    o["selected"] = False
                self.dragging = True
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                self.camera_drag_start_x = self.target_camera_x
                self.camera_drag_start_y = self.target_camera_y
        elif self.interactive_mode == "add_point":
            self.add_point(event.x, event.y)
        elif self.interactive_mode == "add_line":
            if obj_type == "point":
                if self.temp_point is None:
                    self.temp_point = obj
                else:
                    if obj != self.temp_point:
                        self.add_line(self.temp_point, obj)
                    self.temp_point = None
        elif self.interactive_mode == "delete" and obj:
            self.delete_object(obj, obj_type)
        elif self.interactive_mode == "move_point" and obj_type == "point":
            self.selected_objects = [obj]
            self.dragging = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y
        elif self.interactive_mode == "split_line" and obj_type == "line" and obj in self.lines:
            world_x = event.x / self.camera_zoom - self.camera_x
            world_y = event.y / self.camera_zoom - self.camera_y
            new_point = {
                "x": world_x, "y": world_y,
                "color": random.choice(["#58a6ff", "#8b5cf6", "#2ea043"]),
                "size": random.uniform(4, 5),
                "selected": False,
                "id": len(self.points),
                "pulse_offset": random.uniform(0, 2 * math.pi),
                "vx": 0, "vy": 0
            }
            self.split_line(obj, new_point)

    def on_mouse_move(self, event):
        if self.special_modes.get("brush", False) and random.random() < 0.2:
            self.add_point(event.x, event.y)
            return
        if self.dragging:
            if self.interactive_mode == "select":
                dx = (event.x - self.drag_start_x) / self.target_camera_zoom
                dy = (event.y - self.drag_start_y) / self.target_camera_zoom
                self.target_camera_x = self.camera_drag_start_x - dx
                self.target_camera_y = self.camera_drag_start_y - dy
            elif self.interactive_mode == "move_point" and self.selected_objects and self.selected_objects[0] in self.points:
                self.move_point(self.selected_objects[0], event.x, event.y)

    def on_mouse_up(self, event):
        self.dragging = False

    def on_mouse_hover(self, event):
        obj, _ = self.get_object_at(event.x, event.y)
        self.hovered_object = obj
        self.canvas.config(cursor="hand2" if obj else "")

    def on_double_click(self, event):
        obj, obj_type = self.get_object_at(event.x, event.y)
        if obj_type == "line" and obj in self.lines:
            world_x = event.x / self.camera_zoom - self.camera_x
            world_y = event.y / self.camera_zoom - self.camera_y
            new_point = {
                "x": world_x, "y": world_y,
                "color": random.choice(["#58a6ff", "#8b5cf6", "#2ea043"]),
                "size": random.uniform(4, 5),
                "selected": False,
                "id": len(self.points),
                "pulse_offset": random.uniform(0, 2 * math.pi),
                "vx": 0, "vy": 0
            }
            self.split_line(obj, new_point)

    def on_right_click(self, event):
        modes = ["select", "add_point", "add_line", "delete", "move_point", "split_line"]
        current = modes.index(self.interactive_mode)
        self.interactive_mode = modes[(current + 1) % len(modes)]
        self.temp_point = None
        self.update_mode_indicator()

    def zoom_camera(self, event):
        if event.delta > 0:
            self.target_camera_zoom = min(3.0, self.target_camera_zoom * 1.1)
        else:
            self.target_camera_zoom = max(0.5, self.target_camera_zoom / 1.1)

    def reset_camera(self, event=None):
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.target_camera_zoom = 1.0

    def update_mode_indicator(self):
        names = {
            "select": "Выбор (Ctrl+клик)",
            "add_point": "➕ Точка",
            "add_line": "🔗 Линия",
            "delete": "🗑 Удалить",
            "move_point": "✋ Переместить",
            "split_line": "✂ Разбить"
        }
        colors = {
            "select": "#58a6ff",
            "add_point": "#2ea043",
            "add_line": "#ff7b72",
            "delete": "#ff6b6b",
            "move_point": "#f0c674",
            "split_line": "#8b5cf6"
        }
        self.mode_label.config(text=f"Режим: {names[self.interactive_mode]}", fg=colors[self.interactive_mode])

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    # --- ИНИЦИАЛИЗАЦИЯ ---
    def init_stars(self):
        for _ in range(self.star_count):
            self.stars.append({
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "size": random.uniform(0.5, 1.5),
                "brightness": random.uniform(50, 150),
                "twinkle_speed": random.uniform(0.5, 2.0),
                "phase": random.uniform(0, 2 * math.pi)
            })

    def init_particles(self):
        for _ in range(self.particle_count):
            self.particles.append({
                "x": random.randint(50, self.width - 50),
                "y": random.randint(50, self.height - 50),
                "vx": random.uniform(-0.5, 0.5),
                "vy": random.uniform(-0.5, 0.5),
                "size": random.uniform(1.5, 3.0),
                "hue": random.uniform(180, 260),
                "phase": random.uniform(0, 2 * math.pi)
            })

    # --- ОТРИСОВКА ---
    def draw_stars(self):
        for star in self.stars:
            twinkle = 0.5 + 0.5 * math.sin(self.time_offset * star["twinkle_speed"] + star["phase"])
            brightness = int(star["brightness"] * twinkle)
            color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
            x, y = (star["x"] + self.camera_x) * self.camera_zoom, (star["y"] + self.camera_y) * self.camera_zoom
            self.canvas.create_oval(x - star["size"], y - star["size"], x + star["size"], y + star["size"], fill=color, outline="")

    def draw_particles(self):
        for p in self.particles:
            x, y = (p["x"] + self.camera_x) * self.camera_zoom, (p["y"] + self.camera_y) * self.camera_zoom
            size = p["size"] * self.camera_zoom * (1.0 + 0.3 * math.sin(self.time_offset + p["phase"]))
            color = self.hsv_to_hex(p["hue"]/360, 0.5, 0.4)
            self.canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline="")

    def draw_points_and_lines(self):
        for line in self.lines:
            p1, p2 = line["point1"], line["point2"]
            x1, y1 = (p1["x"] + self.camera_x) * self.camera_zoom, (p1["y"] + self.camera_y) * self.camera_zoom
            x2, y2 = (p2["x"] + self.camera_x) * self.camera_zoom, (p2["y"] + self.camera_y) * self.camera_zoom
            width = line["width"] * (1.5 if line in self.selected_objects else 1.0)
            self.canvas.create_line(x1, y1, x2, y2, fill=line["color"], width=width, capstyle=tk.ROUND)

        for point in self.points:
            x, y = (point["x"] + self.camera_x) * self.camera_zoom, (point["y"] + self.camera_y) * self.camera_zoom
            pulse = 1.0 + 0.2 * math.sin(self.time_offset + point["pulse_offset"])
            size = point["size"] * pulse * self.camera_zoom
            color = "#ffffff" if point in self.selected_objects else point["color"]
            self.canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline="")

    def draw_destroy_particles(self):
        for particle in self.destroy_particles[:]:
            x, y = (particle["x"] + self.camera_x) * self.camera_zoom, (particle["y"] + self.camera_y) * self.camera_zoom
            size = particle["size"] * (particle["life"] / particle["max_life"]) * self.camera_zoom
            self.canvas.create_oval(x - size, y - size, x + size, y + size, fill=particle["color"], outline="")
            particle["x"] += particle["vx"] * self.delta_time * 60
            particle["y"] += particle["vy"] * self.delta_time * 60
            particle["life"] -= self.delta_time
            if particle["life"] <= 0:
                self.destroy_particles.remove(particle)

    def draw_special_effects(self):
        if self.special_modes.get("black_hole"):
            x, y = self.black_hole_pos
            x, y = (x + self.camera_x) * self.camera_zoom, (y + self.camera_y) * self.camera_zoom
            for r in range(8, 0, -1):
                radius = r * 8 * self.camera_zoom
                alpha = 255 - r * 30
                color = f"#{alpha:02x}{alpha//2:02x}{alpha//3:02x}"
                self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline=color, width=1)
            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#ffffff", outline="")

        if self.special_modes.get("tornado"):
            x, y = self.tornado_center
            x, y = (x + self.camera_x) * self.camera_zoom, (y + self.camera_y) * self.camera_zoom
            for i in range(6):
                angle = self.time_offset * 0.5 + i * math.pi / 3
                radius = 80 * self.camera_zoom
                x1, y1 = x + radius * math.cos(angle), y + radius * math.sin(angle)
                x2, y2 = x + radius * 1.3 * math.cos(angle + 0.3), y + radius * 1.3 * math.sin(angle + 0.3)
                self.canvas.create_line(x1, y1, x2, y2, fill="#8b5cf6", width=1)

        if self.special_modes.get("rain"):
            for drop in self.rain_drops:
                x, y = (drop["x"] + self.camera_x) * self.camera_zoom, (drop["y"] + self.camera_y) * self.camera_zoom
                size = drop["size"] * self.camera_zoom
                self.canvas.create_line(x, y, x, y + size * 2, fill=drop["color"], width=1)

    def draw_ui_overlay(self):
        mode_names = {
            "select": "🖱 Выбор",
            "add_point": "➕ Точка",
            "add_line": "🔗 Линия",
            "delete": "🗑 Удалить",
            "move_point": "✋ Переместить",
            "split_line": "✂ Разбить"
        }
        text = f"{mode_names.get(self.interactive_mode, '')}"
        if self.current_special_mode is not None:
            modes = list(self.special_modes.keys())
            if self.current_special_mode < len(modes):
                text += f" | 🧠{modes[self.current_special_mode].upper()}"
        text += f" | FPS: {self.fps_display} | Т:{len(self.points)} Л:{len(self.lines)}"
        self.canvas.create_text(10, 10, text=text, fill="#485057", font=("Consolas", 9), anchor=tk.NW)

    def draw_mini_wave(self):
        self.wave_canvas.delete("all")
        width, height = 200, 60
        for i in range(2):
            points = []
            for x in range(0, width + 1, 3):
                y = height/2 + 15 * math.sin(x * 0.08 + self.time_offset * 1.5 + i * 0.3)
                points.extend([x, y])
            alpha = 200 - i * 60
            color = f"#{alpha:02x}{100 + i*20:02x}{180 + i*10:02x}"
            self.wave_canvas.create_line(points, fill=color, width=2 - i*0.5, smooth=True)

    # --- ОБНОВЛЕНИЕ ---
    def update_particles(self):
        for p in self.particles:
            p["x"] += p["vx"] * 0.016 * 60
            p["y"] += p["vy"] * 0.016 * 60
            if p["x"] < 40 or p["x"] > self.width - 40:
                p["vx"] *= -1
                p["x"] = max(40, min(self.width - 40, p["x"]))
            if p["y"] < 40 or p["y"] > self.height - 40:
                p["vy"] *= -1
                p["y"] = max(40, min(self.height - 40, p["y"]))

    def update_camera_smooth(self):
        self.camera_x += (self.target_camera_x - self.camera_x) * self.camera_smoothness
        self.camera_y += (self.target_camera_y - self.camera_y) * self.camera_smoothness
        self.camera_zoom += (self.target_camera_zoom - self.camera_zoom) * self.camera_smoothness

    def setup_left_panel(self):
        Label(self.left_panel, text="🌀 Бесконечное безумие", bg=self.panel_bg, fg=self.text_color, font=("Consolas", 12), anchor=tk.W, pady=15, padx=10).pack(fill=tk.X)
        
        self.cam_info = Label(self.left_panel, text="Камера: 0, 0\nМасштаб: 1.0x", bg=self.panel_bg, fg="#485057", font=("Consolas", 9), anchor=tk.W, padx=10, pady=5)
        self.cam_info.pack(fill=tk.X)
        
        self.fps_label = Label(self.left_panel, text="FPS: 0", bg=self.panel_bg, fg="#2ea043", font=("Consolas", 9), anchor=tk.W, padx=10, pady=5)
        self.fps_label.pack(fill=tk.X)
        
        self.mode_label = Label(self.left_panel, text="Режим: Выбор", bg=self.panel_bg, fg="#58a6ff", font=("Consolas", 10), anchor=tk.W, padx=10, pady=5)
        self.mode_label.pack(fill=tk.X)
        
        self.status_label = Label(self.left_panel, text="F-фрактал S-сохранить L-загрузить P-PNG B-кисть D-дождь U-вселенная", bg=self.panel_bg, fg="#ff7b72", font=("Consolas", 8), anchor=tk.W, padx=10, pady=5, wraplength=250)
        self.status_label.pack(fill=tk.X)
        
        self.wave_canvas = Canvas(self.left_panel, width=200, height=60, bg=self.panel_bg, highlightthickness=0)
        self.wave_canvas.pack(pady=10, padx=10, fill=tk.X)
        
        self.lbl_pulse = Label(self.left_panel, text="Пульс: —", bg=self.panel_bg, fg=self.accent, font=("Consolas", 11), anchor=tk.W, padx=10, pady=5)
        self.lbl_pulse.pack(fill=tk.X)
        
        self.lbl_level = Label(self.left_panel, text="Уровень: —", bg=self.panel_bg, fg="#d2e3fc", font=("Consolas", 11), anchor=tk.W, padx=10, pady=5)
        self.lbl_level.pack(fill=tk.X)
        
        self.lbl_net = Label(self.left_panel, text="Сеть: OK", bg=self.panel_bg, fg="#2ea043", font=("Consolas", 11), anchor=tk.W, padx=10, pady=5)
        self.lbl_net.pack(fill=tk.X)
        
        self.counters = Label(self.left_panel, text="Точек: 0\nЛиний: 0", bg=self.panel_bg, fg="#485057", font=("Consolas", 9), anchor=tk.W, padx=10, pady=5)
        self.counters.pack(fill=tk.X)
        
        self.loading_frame = Frame(self.left_panel, bg=self.panel_bg)
        self.loading_frame.pack(fill=tk.X, padx=10, pady=10)
        self.loading_bar = Canvas(self.loading_frame, width=200, height=4, bg="#21262d", highlightthickness=0)
        self.loading_bar.pack()
        self.loading_rect = self.loading_bar.create_rectangle(0, 0, 0, 4, fill=self.accent)
        
        btn_frame = Frame(self.left_panel, bg=self.panel_bg)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        for text, cmd, color in [
            ("Сброс камеры (Ctrl+0)", self.reset_camera, self.text_color),
            ("Удалить выделенное (Del)", self.delete_selected, "#ff6b6b"),
            ("Выделить всё (Ctrl+A)", self.select_all, "#58a6ff"),
            ("🧠 Странный режим (Пробел)", self.toggle_special_mode, "#ff7b72"),
            # НОВАЯ КНОПКА АВАРИЙНОГО СБРОСА
            ("⚠️ АВАРИЙНЫЙ СБРОС (X)", self.emergency_reset, "#ffffff")
        ]:
            bg_color = "#ff2d8a" if "АВАРИЙНЫЙ" in text else "#21262d"
            fg_color = "#ffffff" if "АВАРИЙНЫЙ" in text else color
            Button(btn_frame, text=text, bg=bg_color, fg=fg_color, font=("Consolas", 9, "bold") if "АВАРИЙНЫЙ" in text else ("Consolas", 9), command=cmd, relief=tk.FLAT, padx=5, pady=3).pack(fill=tk.X, pady=2)
        
        Label(self.left_panel, text="ЛКМ: действие\nПКМ: смена режима\nCtrl+клик: выбор\nДв.клик: разбить линию\n\n⚠️ X - АВАРИЙНЫЙ СБРОС", bg=self.panel_bg, fg="#ff2d8a", font=("Consolas", 8, "bold"), anchor=tk.S, justify=tk.LEFT, padx=10, pady=20).pack(side=tk.BOTTOM, fill=tk.X)

    # --- ГЛАВНЫЙ ЦИКЛ ---
    def animate(self):
        current_time = time.time()
        self.delta_time = current_time - self.last_time
        self.last_time = current_time
        
        self.fps_counter += 1
        self.fps_timer += self.delta_time
        if self.fps_timer >= 1.0:
            self.fps_display = self.fps_counter
            self.fps_counter = 0
            self.fps_timer = 0.0
            self.fps_label.config(text=f"FPS: {self.fps_display}")
        
        self.update_camera_smooth()
        self.time_offset += self.delta_time * 1.5
        self.apply_special_effects()
        self.update_particles()
        
        self.canvas.delete("all")
        self.draw_stars()
        self.draw_particles()
        self.draw_points_and_lines()
        self.draw_destroy_particles()
        self.draw_special_effects()
        self.draw_ui_overlay()
        self.draw_mini_wave()
        
        pulse_val = 50 + 30 * math.sin(self.time_offset)
        self.lbl_pulse.config(text=f"Пульс: {pulse_val:.1f} bpm")
        level_val = 30 + 20 * math.sin(self.time_offset * 0.7 + 1)
        self.lbl_level.config(text=f"Уровень: {level_val:.1f}%")
        self.cam_info.config(text=f"Камера: {int(self.camera_x)}, {int(self.camera_y)}\nМасштаб: {self.camera_zoom:.1f}x")
        self.counters.config(text=f"Точек: {len(self.points)}\nЛиний: {len(self.lines)}")
        load_width = 50 + 150 * abs(math.sin(self.time_offset * 0.3))
        self.loading_bar.coords(self.loading_rect, 0, 0, load_width, 4)
        self.lbl_net.config(text="Сеть: OK" if int(self.time_offset * 10) % 100 < 95 else "Сеть: ПАКЕТЫ", fg="#2ea043" if int(self.time_offset * 10) % 100 < 95 else "#f0883e")
        
        self.root.after(int(self.frame_time * 1000), self.animate)


if __name__ == "__main__":
    root = tk.Tk()
    app = AbstractDashboard(root)
    root.mainloop()