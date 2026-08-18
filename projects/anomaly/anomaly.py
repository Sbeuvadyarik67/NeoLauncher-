import tkinter as tk
from tkinter import Canvas, Frame, Label, Button
import math
import random
import time
import colorsys

class AbstractDashboard:
    def __init__(self, root):
        self.root = root
        self.width = 1360
        self.height = 768
        self.is_fullscreen = False
        
        # Управление FPS
        self.target_fps = 120
        self.frame_time = 1.0 / self.target_fps
        self.last_time = time.time()
        self.delta_time = 0.0
        self.fps_counter = 0
        self.fps_display = 0
        self.fps_timer = 0.0

        # Цвета
        self.bg_color = "#0f1115"
        self.panel_bg = "#161b22"
        self.text_color = "#8b9bb4"
        self.accent = "#58a6ff"

        self.root.title("Абстрактный граф: Космический редактор")
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.configure(bg=self.bg_color)

        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        # Управление камерой
        self.camera_x = 0
        self.camera_y = 0
        self.camera_zoom = 1.0
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.camera_drag_start_x = 0
        self.camera_drag_start_y = 0
        
        # Плавная камера
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.target_camera_zoom = 1.0
        self.camera_smoothness = 0.15

        # НОВЫЕ РЕЖИМЫ (расширенные)
        self.special_modes = {
            "gravity": False,
            "music": False,
            "evolution": False,
            "superposition": False,
            "destroyer": False,
            "neural": False,
            "black_hole": False,      # НОВОЕ: Чёрная дыра
            "fireworks": False,       # НОВОЕ: Фейерверк
            "tornado": False,         # НОВОЕ: Торнадо
            "glitch": False,          # НОВОЕ: Глюки
            "pulse_wave": False,      # НОВОЕ: Волны пульсации
            "dna_spiral": False       # НОВОЕ: Спираль ДНК
        }
        self.current_special_mode = None
        self.gravity_force = 0.01
        self.music_beat = 0
        self.evolution_counter = 0
        self.destroy_particles = []
        self.neural_signals = []
        
        # НОВЫЕ ПАРАМЕТРЫ
        self.black_hole_pos = (self.width/2, self.height/2)
        self.black_hole_strength = 0.5
        self.tornado_center = (self.width/2, self.height/2)
        self.tornado_radius = 200
        self.glitch_offset = 0
        self.pulse_center = (self.width/2, self.height/2)
        self.pulse_radius = 0
        self.dna_points = []
        self.dna_angle = 0

        # Точки и линии
        self.points = []
        self.lines = []
        self.selected_objects = []
        self.hovered_object = None
        
        # Режимы работы
        self.interactive_mode = "select"
        self.temp_point = None
        
        # Счётчики
        self.point_count = 30
        self.line_count = 0

        # Основной контейнер
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель
        self.left_panel = Frame(self.main_frame, width=280, bg=self.panel_bg)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH)
        self.left_panel.pack_propagate(False)

        # Полоска для перетаскивания
        self.drag_bar = Frame(self.left_panel, width=8, bg="#21262d", cursor="fleur")
        self.drag_bar.pack(side=tk.LEFT, fill=tk.BOTH)
        self._make_draggable(self.drag_bar)

        self.setup_left_panel()

        # Центральная область
        self.canvas = Canvas(self.main_frame, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Привязка событий
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
        self.root.bind("<space>", self.toggle_special_mode)

        # Параметры
        self.particles = []
        self.particle_count = 80
        self.time_offset = 0.0
        
        # Звёзды
        self.stars = []
        self.star_count = 60

        self.init_particles()
        self.init_stars()
        self.init_random_points_and_lines()
        self.animate()

    # --- Перетаскивание окна ---
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

    # --- НОВЫЕ СТРАННЫЕ МЕХАНИКИ (расширенные) ---
    
    def toggle_special_mode(self, event=None):
        """Переключение странных режимов по пробелу"""
        modes = list(self.special_modes.keys())
        if self.current_special_mode is None:
            self.current_special_mode = 0
        else:
            self.current_special_mode = (self.current_special_mode + 1) % len(modes)
        
        # Сброс всех режимов
        for key in self.special_modes:
            self.special_modes[key] = False
        
        if self.current_special_mode is not None:
            mode_name = modes[self.current_special_mode]
            self.special_modes[mode_name] = True
            self.status_label.config(text=f"🧠 Режим: {mode_name.upper()} (Пробел для смены)")
            
            # Специальные инициализации
            if mode_name == "destroyer":
                self.destroy_particles = []
            elif mode_name == "neural":
                self.neural_signals = []
            elif mode_name == "fireworks":
                self.create_fireworks()
            elif mode_name == "dna_spiral":
                self.create_dna_spiral()

    def apply_special_effects(self):
        """Применение эффектов странных режимов"""
        
        # 1. ГРАВИТАЦИЯ
        if self.special_modes.get("gravity", False):
            for i, p1 in enumerate(self.points):
                for j, p2 in enumerate(self.points):
                    if i >= j: continue
                    dx = p2["x"] - p1["x"]
                    dy = p2["y"] - p1["y"]
                    dist = math.hypot(dx, dy)
                    if dist < 300 and dist > 10:
                        force = self.gravity_force / (dist + 1)
                        p1["vx"] += dx * force * 0.1
                        p1["vy"] += dy * force * 0.1
                        p2["vx"] -= dx * force * 0.1
                        p2["vy"] -= dy * force * 0.1

        # 2. МУЗЫКА
        if self.special_modes.get("music", False):
            self.music_beat += self.delta_time * 2
            beat = math.sin(self.music_beat) * 0.5 + 0.5
            for i, point in enumerate(self.points):
                point["size"] = 5 + 8 * (0.5 + 0.5 * math.sin(self.music_beat + i * 0.5))
                h = (i / max(1, len(self.points)) + beat * 0.2) % 1.0
                point["color"] = self.hsv_to_hex(h, 0.8, 0.6)

        # 3. ЭВОЛЮЦИЯ
        if self.special_modes.get("evolution", False):
            self.evolution_counter += self.delta_time
            if self.evolution_counter > 2.0 and len(self.points) < 100:
                self.evolution_counter = 0
                if self.points:
                    parent = random.choice(self.points)
                    new_x = parent["x"] + random.uniform(-50, 50)
                    new_y = parent["y"] + random.uniform(-50, 50)
                    new_color = self.mutate_color(parent["color"])
                    self.points.append({
                        "x": new_x, "y": new_y,
                        "color": new_color,
                        "size": random.uniform(4, 8),
                        "selected": False,
                        "id": len(self.points),
                        "pulse_offset": random.uniform(0, 2 * math.pi),
                        "vx": random.uniform(-0.5, 0.5),
                        "vy": random.uniform(-0.5, 0.5)
                    })
                    self.add_line(parent, self.points[-1])

        # 4. СУПЕРПОЗИЦИЯ
        if self.special_modes.get("superposition", False):
            for point in self.points:
                if "ghost_x" not in point:
                    point["ghost_x"] = point["x"] + random.uniform(-30, 30)
                    point["ghost_y"] = point["y"] + random.uniform(-30, 30)
                point["ghost_x"] -= point.get("vx", 0) * 0.5
                point["ghost_y"] -= point.get("vy", 0) * 0.5
                point["ghost_x"] += (point["x"] - point["ghost_x"]) * 0.01
                point["ghost_y"] += (point["y"] - point["ghost_y"]) * 0.01

        # 5. НЕЙРОСЕТЬ
        if self.special_modes.get("neural", False):
            if random.random() < 0.02 and self.points:
                start = random.choice(self.points)
                end = random.choice(self.points)
                if start != end:
                    self.neural_signals.append({
                        "start": start,
                        "end": end,
                        "progress": 0,
                        "speed": random.uniform(0.02, 0.05),
                        "color": random.choice(["#ff6b6b", "#ffd93d", "#6bcfff", "#a66cff"])
                    })
            
            for signal in self.neural_signals[:]:
                signal["progress"] += signal["speed"]
                if signal["progress"] > 1:
                    self.neural_signals.remove(signal)

        # 6. НОВОЕ: ЧЁРНАЯ ДЫРА
        if self.special_modes.get("black_hole", False):
            bh_x, bh_y = self.black_hole_pos
            for point in self.points:
                dx = bh_x - point["x"]
                dy = bh_y - point["y"]
                dist = math.hypot(dx, dy)
                if dist > 10:
                    force = self.black_hole_strength / (dist * 0.5 + 1)
                    point["vx"] += dx * force * 0.05
                    point["vy"] += dy * force * 0.05
                    # Если точка слишком близко - поглощаем
                    if dist < 20:
                        self.destroy_point(point)
                        # Создаём эффект поглощения
                        for _ in range(5):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(1, 3)
                            self.destroy_particles.append({
                                "x": point["x"], "y": point["y"],
                                "vx": math.cos(angle) * speed,
                                "vy": math.sin(angle) * speed,
                                "size": random.uniform(2, 4),
                                "color": "#ffffff",
                                "life": random.uniform(0.3, 0.8),
                                "max_life": random.uniform(0.3, 0.8)
                            })
            
            # Визуализация чёрной дыры
            self.black_hole_pos = (self.width/2 + 50 * math.sin(self.time_offset * 0.3),
                                   self.height/2 + 50 * math.cos(self.time_offset * 0.5))

        # 7. НОВОЕ: ТОРНАДО
        if self.special_modes.get("tornado", False):
            tx, ty = self.tornado_center
            for point in self.points:
                dx = point["x"] - tx
                dy = point["y"] - ty
                dist = math.hypot(dx, dy)
                if dist < self.tornado_radius:
                    angle = math.atan2(dy, dx) + self.time_offset * 0.5
                    force = (1 - dist / self.tornado_radius) * 0.1
                    point["vx"] += math.cos(angle + math.pi/2) * force * 2
                    point["vy"] += math.sin(angle + math.pi/2) * force * 2
                    # Поднимаем точки вверх
                    point["vy"] -= 0.05 * (1 - dist / self.tornado_radius)

        # 8. НОВОЕ: ГЛЮКИ
        if self.special_modes.get("glitch", False):
            self.glitch_offset += self.delta_time * 10
            for point in self.points:
                if random.random() < 0.01:
                    point["x"] += random.uniform(-20, 20)
                    point["y"] += random.uniform(-20, 20)
                # Мерцание цвета
                if random.random() < 0.005:
                    point["color"] = random.choice(["#ff0000", "#00ff00", "#0000ff", "#ff00ff", "#00ffff"])

        # 9. НОВОЕ: ВОЛНЫ ПУЛЬСАЦИИ
        if self.special_modes.get("pulse_wave", False):
            self.pulse_radius += self.delta_time * 100
            if self.pulse_radius > 800:
                self.pulse_radius = 0
                self.pulse_center = (random.randint(100, self.width-100),
                                     random.randint(100, self.height-100))
            
            cx, cy = self.pulse_center
            for point in self.points:
                dx = point["x"] - cx
                dy = point["y"] - cy
                dist = math.hypot(dx, dy)
                if abs(dist - self.pulse_radius) < 50:
                    # Отталкивание от волны
                    angle = math.atan2(dy, dx)
                    force = 2 * (1 - abs(dist - self.pulse_radius) / 50)
                    point["vx"] += math.cos(angle) * force * 0.5
                    point["vy"] += math.sin(angle) * force * 0.5

        # 10. НОВОЕ: СПИРАЛЬ ДНК
        if self.special_modes.get("dna_spiral", False):
            self.dna_angle += self.delta_time * 0.5
            for i, point in enumerate(self.points):
                t = i / max(1, len(self.points))
                angle = self.dna_angle + t * 4 * math.pi
                radius = 100 + 50 * math.sin(t * 10 + self.time_offset)
                target_x = self.width/2 + radius * math.cos(angle)
                target_y = self.height/2 + (t - 0.5) * 400
                point["x"] += (target_x - point["x"]) * 0.02
                point["y"] += (target_y - point["y"]) * 0.02

    def create_fireworks(self):
        """Создание фейерверка"""
        for _ in range(20):
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            color = random.choice(["#ff6b6b", "#ffd93d", "#6bcfff", "#a66cff", "#ff44ff", "#44ff44"])
            for _ in range(15):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 8)
                self.destroy_particles.append({
                    "x": x, "y": y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "size": random.uniform(2, 5),
                    "color": color,
                    "life": random.uniform(1.0, 2.5),
                    "max_life": random.uniform(1.0, 2.5)
                })

    def create_dna_spiral(self):
        """Создание спирали ДНК"""
        # Очищаем старые точки
        self.points = []
        self.lines = []
        for i in range(30):
            t = i / 30
            angle = t * 4 * math.pi
            radius = 100 + 30 * math.sin(t * 10)
            x = self.width/2 + radius * math.cos(angle)
            y = self.height/2 + (t - 0.5) * 400
            color = "#58a6ff" if i % 2 == 0 else "#ff7b72"
            self.points.append({
                "x": x, "y": y,
                "color": color,
                "size": random.uniform(4, 7),
                "selected": False,
                "id": i,
                "pulse_offset": random.uniform(0, 2 * math.pi),
                "vx": 0,
                "vy": 0
            })
        # Создаём связи
        for i in range(len(self.points) - 1):
            self.add_line(self.points[i], self.points[i+1])
            if i < len(self.points) - 2:
                self.add_line(self.points[i], self.points[i+2])

    def mutate_color(self, color):
        hex_color = color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        h = (h + random.uniform(-0.1, 0.1)) % 1.0
        s = min(1, max(0.3, s + random.uniform(-0.2, 0.2)))
        v = min(1, max(0.3, v + random.uniform(-0.2, 0.2)))
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    @staticmethod
    def hsv_to_hex(h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    # --- Новая механика взрыва ---
    def destroy_point(self, point):
        if point in self.points:
            for _ in range(30):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 5)
                self.destroy_particles.append({
                    "x": point["x"],
                    "y": point["y"],
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "size": random.uniform(2, 6),
                    "color": point["color"],
                    "life": random.uniform(0.5, 2.0),
                    "max_life": random.uniform(0.5, 2.0)
                })
            self.delete_object(point, "point")

    # --- Остальные методы ---
    def init_random_points_and_lines(self):
        for _ in range(self.point_count):
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            color = random.choice(["#58a6ff", "#8b5cf6", "#2ea043", "#ff7b72", "#f0c674", "#79c0ff"])
            size = random.uniform(4, 8)
            self.points.append({
                "x": x, "y": y,
                "color": color,
                "size": size,
                "selected": False,
                "id": len(self.points),
                "pulse_offset": random.uniform(0, 2 * math.pi),
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(-0.3, 0.3)
            })
        
        for _ in range(20):
            if len(self.points) >= 2:
                p1 = random.choice(self.points)
                p2 = random.choice(self.points)
                if p1 != p2 and not self.line_exists(p1, p2):
                    color = random.choice(["#58a6ff", "#8b5cf6", "#ff7b72", "#2ea043", "#f0c674"])
                    self.lines.append({
                        "point1": p1,
                        "point2": p2,
                        "color": color,
                        "width": random.uniform(1, 3),
                        "selected": False
                    })
        self.line_count = len(self.lines)

    def line_exists(self, p1, p2):
        for line in self.lines:
            if (line["point1"] == p1 and line["point2"] == p2) or \
               (line["point1"] == p2 and line["point2"] == p1):
                return True
        return False

    def get_object_at(self, x, y):
        world_x = x / self.camera_zoom - self.camera_x
        world_y = y / self.camera_zoom - self.camera_y
        
        for point in self.points:
            dist = math.hypot(point["x"] - world_x, point["y"] - world_y)
            if dist < point["size"] * 2:
                return point, "point"
        
        for line in self.lines:
            p1, p2 = line["point1"], line["point2"]
            dist = self.distance_to_segment(world_x, world_y, p1["x"], p1["y"], p2["x"], p2["y"])
            if dist < 10 / self.camera_zoom:
                return line, "line"
        
        return None, None

    def distance_to_segment(self, px, py, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        
        t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))
        
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(px - proj_x, py - proj_y)

    def add_point(self, x, y):
        world_x = x / self.camera_zoom - self.camera_x
        world_y = y / self.camera_zoom - self.camera_y
        
        color = random.choice(["#58a6ff", "#8b5cf6", "#2ea043", "#ff7b72", "#f0c674", "#79c0ff"])
        point = {
            "x": world_x, "y": world_y,
            "color": color,
            "size": random.uniform(4, 8),
            "selected": False,
            "id": len(self.points),
            "pulse_offset": random.uniform(0, 2 * math.pi),
            "vx": random.uniform(-0.3, 0.3),
            "vy": random.uniform(-0.3, 0.3)
        }
        self.points.append(point)
        self.selected_objects = [point]
        return point

    def add_line(self, point1, point2):
        if point1 and point2 and point1 != point2:
            if not self.line_exists(point1, point2):
                color = random.choice(["#58a6ff", "#8b5cf6", "#ff7b72", "#2ea043", "#f0c674"])
                line = {
                    "point1": point1,
                    "point2": point2,
                    "color": color,
                    "width": random.uniform(1, 3),
                    "selected": False
                }
                self.lines.append(line)
                self.line_count += 1
                return line
        return None

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
        world_x = new_x / self.camera_zoom - self.camera_x
        world_y = new_y / self.camera_zoom - self.camera_y
        point["x"] = world_x
        point["y"] = world_y

    def split_line(self, line, new_point):
        if line in self.lines:
            p1, p2 = line["point1"], line["point2"]
            self.lines.remove(line)
            self.add_line(p1, new_point)
            self.add_line(new_point, p2)
            self.points.append(new_point)

    # --- Обработчики событий ---
    def on_mouse_down(self, event):
        obj, obj_type = self.get_object_at(event.x, event.y)
        
        if self.special_modes.get("destroyer", False) and obj_type == "point":
            self.destroy_point(obj)
            return
        
        if self.interactive_mode == "select":
            if obj:
                if event.state & 0x0004:
                    if obj in self.selected_objects:
                        self.selected_objects.remove(obj)
                        if "selected" in obj:
                            obj["selected"] = False
                    else:
                        self.selected_objects.append(obj)
                        if "selected" in obj:
                            obj["selected"] = True
                else:
                    self.selected_objects = [obj] if obj else []
                    for o in self.points + self.lines:
                        if "selected" in o:
                            o["selected"] = o in self.selected_objects
                self.dragging = False
            else:
                self.selected_objects = []
                for o in self.points + self.lines:
                    if "selected" in o:
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
        
        elif self.interactive_mode == "delete":
            if obj:
                self.delete_object(obj, obj_type)
        
        elif self.interactive_mode == "move_point":
            if obj_type == "point":
                self.selected_objects = [obj]
                self.dragging = True
                self.drag_start_x = event.x
                self.drag_start_y = event.y
        
        elif self.interactive_mode == "split_line":
            if obj_type == "line" and obj in self.lines:
                world_x = event.x / self.camera_zoom - self.camera_x
                world_y = event.y / self.camera_zoom - self.camera_y
                new_point = {
                    "x": world_x, "y": world_y,
                    "color": random.choice(["#58a6ff", "#8b5cf6", "#2ea043", "#ff7b72"]),
                    "size": random.uniform(4, 6),
                    "selected": False,
                    "id": len(self.points),
                    "pulse_offset": random.uniform(0, 2 * math.pi),
                    "vx": 0,
                    "vy": 0
                }
                self.split_line(obj, new_point)

    def on_mouse_move(self, event):
        if self.dragging:
            if self.interactive_mode == "select":
                dx = (event.x - self.drag_start_x) / self.target_camera_zoom
                dy = (event.y - self.drag_start_y) / self.target_camera_zoom
                self.target_camera_x = self.camera_drag_start_x - dx
                self.target_camera_y = self.camera_drag_start_y - dy
            elif self.interactive_mode == "move_point" and self.selected_objects:
                if self.selected_objects[0] in self.points:
                    self.move_point(self.selected_objects[0], event.x, event.y)

    def on_mouse_up(self, event):
        self.dragging = False

    def on_mouse_hover(self, event):
        obj, obj_type = self.get_object_at(event.x, event.y)
        if obj != self.hovered_object:
            self.hovered_object = obj
            if obj:
                self.canvas.config(cursor="hand2")
            else:
                self.canvas.config(cursor="")

    def on_double_click(self, event):
        obj, obj_type = self.get_object_at(event.x, event.y)
        if obj_type == "line" and obj in self.lines:
            world_x = event.x / self.camera_zoom - self.camera_x
            world_y = event.y / self.camera_zoom - self.camera_y
            new_point = {
                "x": world_x, "y": world_y,
                "color": random.choice(["#58a6ff", "#8b5cf6", "#2ea043", "#ff7b72"]),
                "size": random.uniform(4, 6),
                "selected": False,
                "id": len(self.points),
                "pulse_offset": random.uniform(0, 2 * math.pi),
                "vx": 0,
                "vy": 0
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
            self.target_camera_zoom *= 1.1
        else:
            self.target_camera_zoom /= 1.1
        self.target_camera_zoom = max(0.5, min(3.0, self.target_camera_zoom))

    def reset_camera(self, event=None):
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.target_camera_zoom = 1.0

    def update_mode_indicator(self):
        mode_names = {
            "select": "Выбор (Ctrl+клик)",
            "add_point": "Добавить точку",
            "add_line": "Создать линию",
            "delete": "Удалить",
            "move_point": "Переместить точку",
            "split_line": "Разбить линию (дв. клик)"
        }
        mode_colors = {
            "select": "#58a6ff",
            "add_point": "#2ea043",
            "add_line": "#ff7b72",
            "delete": "#ff6b6b",
            "move_point": "#f0c674",
            "split_line": "#8b5cf6"
        }
        self.mode_label.config(
            text=f"Режим: {mode_names[self.interactive_mode]}",
            fg=mode_colors[self.interactive_mode]
        )

    # --- Левая панель ---
    def setup_left_panel(self):
        lbl_title = Label(
            self.left_panel, text="Абстрактный граф\nКосмический редактор",
            bg=self.panel_bg, fg=self.text_color,
            font=("Consolas", 12), justify=tk.LEFT,
            anchor=tk.W, pady=15, padx=10
        )
        lbl_title.pack(fill=tk.X)

        self.cam_info = Label(
            self.left_panel,
            text="Камера: 0, 0\nМасштаб: 1.0x",
            bg=self.panel_bg,
            fg="#485057",
            font=("Consolas", 9),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.cam_info.pack(fill=tk.X)

        self.fps_label = Label(
            self.left_panel,
            text="FPS: 0",
            bg=self.panel_bg,
            fg="#2ea043",
            font=("Consolas", 9),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.fps_label.pack(fill=tk.X)

        self.mode_label = Label(
            self.left_panel,
            text="Режим: Выбор (Ctrl+клик)",
            bg=self.panel_bg,
            fg="#58a6ff",
            font=("Consolas", 10),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.mode_label.pack(fill=tk.X)

        self.status_label = Label(
            self.left_panel,
            text="Пробел для странных режимов",
            bg=self.panel_bg,
            fg="#ff7b72",
            font=("Consolas", 9),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.status_label.pack(fill=tk.X)

        self.wave_canvas = Canvas(
            self.left_panel,
            width=200, height=60,
            bg=self.panel_bg,
            highlightthickness=0
        )
        self.wave_canvas.pack(pady=10, padx=10, fill=tk.X)

        self.lbl_pulse = Label(self.left_panel, text="Пульс: —", bg=self.panel_bg,
                               fg=self.accent, font=("Consolas", 11),
                               anchor=tk.W, padx=10, pady=5)
        self.lbl_pulse.pack(fill=tk.X)

        self.lbl_level = Label(self.left_panel, text="Уровень: —", bg=self.panel_bg,
                               fg="#d2e3fc", font=("Consolas", 11),
                               anchor=tk.W, padx=10, pady=5)
        self.lbl_level.pack(fill=tk.X)

        self.lbl_net = Label(self.left_panel, text="Сеть: OK", bg=self.panel_bg,
                             fg="#2ea043", font=("Consolas", 11),
                             anchor=tk.W, padx=10, pady=5)
        self.lbl_net.pack(fill=tk.X)

        self.counters = Label(
            self.left_panel,
            text="Точек: 0\nЛиний: 0",
            bg=self.panel_bg,
            fg="#485057",
            font=("Consolas", 9),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.counters.pack(fill=tk.X)

        self.loading_frame = Frame(self.left_panel, bg=self.panel_bg)
        self.loading_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.loading_bar = Canvas(
            self.loading_frame,
            width=200, height=4,
            bg="#21262d",
            highlightthickness=0
        )
        self.loading_bar.pack()
        self.loading_rect = self.loading_bar.create_rectangle(
            0, 0, 0, 4,
            fill=self.accent
        )

        btn_frame = Frame(self.left_panel, bg=self.panel_bg)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        btn_reset = Button(
            btn_frame,
            text="Сброс камеры (Ctrl+0)",
            bg="#21262d",
            fg=self.text_color,
            font=("Consolas", 9),
            command=self.reset_camera,
            relief=tk.FLAT,
            padx=5,
            pady=3
        )
        btn_reset.pack(fill=tk.X, pady=2)

        btn_clear = Button(
            btn_frame,
            text="Удалить выделенное (Del)",
            bg="#21262d",
            fg="#ff6b6b",
            font=("Consolas", 9),
            command=self.delete_selected,
            relief=tk.FLAT,
            padx=5,
            pady=3
        )
        btn_clear.pack(fill=tk.X, pady=2)

        btn_select_all = Button(
            btn_frame,
            text="Выделить всё (Ctrl+A)",
            bg="#21262d",
            fg="#58a6ff",
            font=("Consolas", 9),
            command=self.select_all,
            relief=tk.FLAT,
            padx=5,
            pady=3
        )
        btn_select_all.pack(fill=tk.X, pady=2)

        btn_special = Button(
            btn_frame,
            text="🧠 Странный режим (Пробел)",
            bg="#21262d",
            fg="#ff7b72",
            font=("Consolas", 9),
            command=self.toggle_special_mode,
            relief=tk.FLAT,
            padx=5,
            pady=3
        )
        btn_special.pack(fill=tk.X, pady=2)

        spacer = Frame(self.left_panel, height=10, bg=self.panel_bg)
        spacer.pack()

        lbl_foot = Label(self.left_panel, 
                         text="ЛКМ: действие\nПКМ: смена режима\nCtrl+клик: выбор\nДв.клик: разбить линию\nDel: удалить выделенное\nПробел: 10 странных режимов!",
                         bg=self.panel_bg, fg="#485057",
                         font=("Consolas", 8), anchor=tk.S,
                         justify=tk.LEFT, padx=10, pady=20)
        lbl_foot.pack(side=tk.BOTTOM, fill=tk.X)

    # --- Звёзды ---
    def init_stars(self):
        for _ in range(self.star_count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.uniform(0.5, 1.5)
            brightness = random.uniform(50, 150)
            twinkle_speed = random.uniform(0.5, 2.0)
            self.stars.append({
                "x": x, "y": y,
                "size": size,
                "brightness": brightness,
                "twinkle_speed": twinkle_speed,
                "phase": random.uniform(0, 2 * math.pi)
            })

    # --- Частицы ---
    def init_particles(self):
        for _ in range(self.particle_count):
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            vx = random.uniform(-0.8, 0.8)
            vy = random.uniform(-0.8, 0.8)
            size = random.uniform(1.5, 3.5)
            hue = random.uniform(180, 260)
            phase = random.uniform(0, 2 * math.pi)
            self.particles.append({
                "x": x, "y": y, "vx": vx, "vy": vy,
                "size": size, "hue": hue, "phase": phase
            })

    @staticmethod
    def hsl_to_hex(h, s, l):
        h = h % 360
        s = max(0, min(100, s)) / 100.0
        l = max(0, min(100, l)) / 100.0
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60.0) % 2 - 1))
        m = l - c / 2

        if 0 <= h < 60: r, g, b = c, x, 0
        elif 60 <= h < 120: r, g, b = x, c, 0
        elif 120 <= h < 180: r, g, b = 0, c, x
        elif 180 <= h < 240: r, g, b = 0, x, c
        elif 240 <= h < 300: r, g, b = x, 0, c
        else: r, g, b = c, 0, x

        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    # --- Отрисовка ---
    def draw_stars(self):
        for star in self.stars:
            twinkle = 0.5 + 0.5 * math.sin(self.time_offset * star["twinkle_speed"] + star["phase"])
            brightness = int(star["brightness"] * twinkle)
            color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
            
            x = (star["x"] + self.camera_x) * self.camera_zoom
            y = (star["y"] + self.camera_y) * self.camera_zoom
            
            self.canvas.create_oval(
                x - star["size"], y - star["size"],
                x + star["size"], y + star["size"],
                fill=color, outline=""
            )

    def draw_destroy_particles(self):
        for particle in self.destroy_particles[:]:
            x = (particle["x"] + self.camera_x) * self.camera_zoom
            y = (particle["y"] + self.camera_y) * self.camera_zoom
            size = particle["size"] * (particle["life"] / particle["max_life"]) * self.camera_zoom
            
            self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=particle["color"],
                outline=""
            )
            
            particle["x"] += particle["vx"] * self.delta_time * 60
            particle["y"] += particle["vy"] * self.delta_time * 60
            particle["life"] -= self.delta_time
            particle["vx"] *= 0.98
            particle["vy"] *= 0.98
            
            if particle["life"] <= 0:
                self.destroy_particles.remove(particle)

    def draw_points_and_lines(self):
        # Рисуем линии
        for line in self.lines:
            p1, p2 = line["point1"], line["point2"]
            x1 = (p1["x"] + self.camera_x) * self.camera_zoom
            y1 = (p1["y"] + self.camera_y) * self.camera_zoom
            x2 = (p2["x"] + self.camera_x) * self.camera_zoom
            y2 = (p2["y"] + self.camera_y) * self.camera_zoom
            
            is_selected = line in self.selected_objects
            width = line["width"] * (1.5 if is_selected else 1.0)
            color = "#ffffff" if is_selected else line["color"]
            
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=line["color"],
                width=width * 3,
                capstyle=tk.ROUND,
                stipple="gray25"
            )
            
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=width,
                capstyle=tk.ROUND
            )
            
            if self.time_offset % 1 < 0.3:
                t = (self.time_offset % 1) / 0.3
                px = x1 + (x2 - x1) * t
                py = y1 + (y2 - y1) * t
                self.canvas.create_oval(
                    px - 3, py - 3,
                    px + 3, py + 3,
                    fill="#ffffff", outline=""
                )

        # Рисуем точки
        for point in self.points:
            x = (point["x"] + self.camera_x) * self.camera_zoom
            y = (point["y"] + self.camera_y) * self.camera_zoom
            
            pulse = 1.0 + 0.3 * math.sin(self.time_offset + point["pulse_offset"])
            size = point["size"] * pulse * self.camera_zoom
            
            is_selected = point in self.selected_objects
            is_hovered = point == self.hovered_object
            
            if self.special_modes.get("superposition", False) and "ghost_x" in point:
                gx = (point["ghost_x"] + self.camera_x) * self.camera_zoom
                gy = (point["ghost_y"] + self.camera_y) * self.camera_zoom
                self.canvas.create_oval(
                    gx - size * 0.5, gy - size * 0.5,
                    gx + size * 0.5, gy + size * 0.5,
                    fill=point["color"],
                    outline="",
                    stipple="gray50"
                )
            
            self.canvas.create_oval(
                x - size * 3, y - size * 3,
                x + size * 3, y + size * 3,
                fill=point["color"],
                outline="",
                stipple="gray25"
            )
            
            color = "#ffffff" if is_selected or is_hovered else point["color"]
            outline = "#ffffff" if is_selected else ""
            width = 2 if is_selected else 0
            
            self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=color,
                outline=outline,
                width=width
            )

    def draw_neural_signals(self):
        for signal in self.neural_signals:
            p1, p2 = signal["start"], signal["end"]
            t = signal["progress"]
            
            x1 = (p1["x"] + self.camera_x) * self.camera_zoom
            y1 = (p1["y"] + self.camera_y) * self.camera_zoom
            x2 = (p2["x"] + self.camera_x) * self.camera_zoom
            y2 = (p2["y"] + self.camera_y) * self.camera_zoom
            
            px = x1 + (x2 - x1) * t
            py = y1 + (y2 - y1) * t
            
            size = 5 * (1 - t) + 3
            self.canvas.create_oval(
                px - size, py - size,
                px + size, py + size,
                fill=signal["color"],
                outline=""
            )
            
            for i in range(5):
                tt = max(0, t - i * 0.02)
                sx = x1 + (x2 - x1) * tt
                sy = y1 + (y2 - y1) * tt
                self.canvas.create_oval(
                    sx - 2, sy - 2,
                    sx + 2, sy + 2,
                    fill=signal["color"],
                    outline=""
                )

    def draw_special_effects(self):
        """Рисование спецэффектов для новых режимов"""
        
        # Чёрная дыра
        if self.special_modes.get("black_hole", False):
            x, y = self.black_hole_pos
            x = (x + self.camera_x) * self.camera_zoom
            y = (y + self.camera_y) * self.camera_zoom
            for r in range(10, 0, -1):
                radius = r * 10 * self.camera_zoom
                alpha = 255 - r * 25
                color = f"#{alpha:02x}{alpha//2:02x}{alpha//3:02x}"
                self.canvas.create_oval(
                    x - radius, y - radius,
                    x + radius, y + radius,
                    outline=color, width=2
                )
            self.canvas.create_oval(
                x - 5, y - 5,
                x + 5, y + 5,
                fill="#ffffff", outline=""
            )

        # Торнадо
        if self.special_modes.get("tornado", False):
            x, y = self.tornado_center
            x = (x + self.camera_x) * self.camera_zoom
            y = (y + self.camera_y) * self.camera_zoom
            for i in range(8):
                angle = self.time_offset * 0.5 + i * math.pi / 4
                radius = 100 * self.camera_zoom
                x1 = x + radius * math.cos(angle)
                y1 = y + radius * math.sin(angle)
                x2 = x + radius * 1.5 * math.cos(angle + 0.3)
                y2 = y + radius * 1.5 * math.sin(angle + 0.3)
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill="#8b5cf6", width=2, stipple="gray50"
                )

        # Волны пульсации
        if self.special_modes.get("pulse_wave", False):
            cx, cy = self.pulse_center
            cx = (cx + self.camera_x) * self.camera_zoom
            cy = (cy + self.camera_y) * self.camera_zoom
            radius = self.pulse_radius * self.camera_zoom
            self.canvas.create_oval(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                outline="#00d4ff", width=2, stipple="gray50"
            )
            self.canvas.create_oval(
                cx - radius - 20, cy - radius - 20,
                cx + radius + 20, cy + radius + 20,
                outline="#00d4ff", width=1, stipple="gray25"
            )

    def draw_particles(self):
        for p in self.particles:
            x = (p["x"] + self.camera_x) * self.camera_zoom
            y = (p["y"] + self.camera_y) * self.camera_zoom
            size = p["size"] * self.camera_zoom
            
            pulse = 1.0 + 0.4 * math.sin(self.time_offset + p["phase"])
            draw_size = size * pulse
            color = self.hsl_to_hex(p["hue"], 60, 45)

            self.canvas.create_oval(
                x - draw_size * 2, y - draw_size * 2,
                x + draw_size * 2, y + draw_size * 2,
                fill=self.hsl_to_hex(p["hue"], 50, 20),
                outline="",
                stipple="gray25"
            )

            self.canvas.create_oval(
                x - draw_size, y - draw_size,
                x + draw_size, y + draw_size,
                fill=color, outline=""
            )

    def draw_ui_overlay(self):
        mode_text = {
            "select": "🖱 Выбор",
            "add_point": "➕ Точка",
            "add_line": "🔗 Линия",
            "delete": "🗑 Удалить",
            "move_point": "✋ Переместить",
            "split_line": "✂ Разбить"
        }
        
        special_text = ""
        if self.current_special_mode is not None:
            modes = list(self.special_modes.keys())
            if self.current_special_mode < len(modes):
                special_text = f" | 🧠{modes[self.current_special_mode].upper()}"
        
        self.canvas.create_text(
            10, 10,
            text=f"{mode_text.get(self.interactive_mode, '')}{special_text} | FPS: {self.fps_display} | Т: {len(self.points)} | Л: {len(self.lines)}",
            fill="#485057",
            font=("Consolas", 10),
            anchor=tk.NW
        )

        if self.temp_point:
            x = (self.temp_point["x"] + self.camera_x) * self.camera_zoom
            y = (self.temp_point["y"] + self.camera_y) * self.camera_zoom
            self.canvas.create_text(
                10, 30,
                text="Выберите вторую точку",
                fill="#ff7b72",
                font=("Consolas", 9),
                anchor=tk.NW
            )
            self.canvas.create_oval(
                x - 12, y - 12,
                x + 12, y + 12,
                outline="#ff7b72",
                width=2,
                dash=(4, 4)
            )

        if self.selected_objects:
            count = len(self.selected_objects)
            points_count = sum(1 for obj in self.selected_objects if obj in self.points)
            lines_count = sum(1 for obj in self.selected_objects if obj in self.lines)
            self.canvas.create_text(
                10, 50,
                text=f"Выделено: {count} ({points_count} т, {lines_count} л)",
                fill="#58a6ff",
                font=("Consolas", 9),
                anchor=tk.NW
            )

    def draw_mini_wave(self):
        self.wave_canvas.delete("all")
        width = 200
        height = 60
        
        for i in range(3):
            offset = i * 0.3
            y_offset = 8 * math.sin(self.time_offset * 0.7 + i)
            points = []
            for x in range(0, width + 1, 2):
                y = height/2 + 15 * math.sin(x * 0.08 + self.time_offset * 1.5 + offset) + y_offset
                points.extend([x, y])
            
            alpha = 200 - i * 40
            color = f"#{alpha:02x}{100 + i*20:02x}{180 + i*10:02x}"
            self.wave_canvas.create_line(points, fill=color, width=2 - i*0.3, smooth=True)

    # --- Обновление ---
    def update_particles(self):
        for p in self.particles:
            speed_mod = 1.0 + 0.3 * math.sin(self.time_offset)
            p["x"] += p["vx"] * speed_mod * 0.016 * 60
            p["y"] += p["vy"] * speed_mod * 0.016 * 60

            if p["x"] < 40 or p["x"] > self.width - 40:
                p["vx"] *= -1
                p["x"] = max(40, min(self.width - 40, p["x"]))
            if p["y"] < 40 or p["y"] > self.height - 40:
                p["vy"] *= -1
                p["y"] = max(40, min(self.height - 40, p["y"]))

            p["vx"] += random.uniform(-0.005, 0.005)
            p["vy"] += random.uniform(-0.005, 0.005)

            speed = math.hypot(p["vx"], p["vy"])
            max_speed = 1.5
            if speed > max_speed:
                p["vx"] = (p["vx"] / speed) * max_speed
                p["vy"] = (p["vy"] / speed) * max_speed

    def update_camera_smooth(self):
        self.camera_x += (self.target_camera_x - self.camera_x) * self.camera_smoothness
        self.camera_y += (self.target_camera_y - self.camera_y) * self.camera_smoothness
        self.camera_zoom += (self.target_camera_zoom - self.camera_zoom) * self.camera_smoothness

    def animate(self):
        current_time = time.time()
        self.delta_time = current_time - self.last_time
        self.last_time = current_time
        
        # Обновляем FPS
        self.fps_counter += 1
        self.fps_timer += self.delta_time
        if self.fps_timer >= 1.0:
            self.fps_display = self.fps_counter
            self.fps_counter = 0
            self.fps_timer = 0.0
            self.fps_label.config(text=f"FPS: {self.fps_display}")
        
        # Обновляем камеру
        self.update_camera_smooth()
        
        # Обновляем время
        self.time_offset += self.delta_time * 1.5
        
        # Применяем странные эффекты
        self.apply_special_effects()
        
        # Обновляем частицы
        self.update_particles()
        
        # Отрисовка
        self.canvas.delete("all")
        self.draw_stars()
        self.draw_particles()
        self.draw_points_and_lines()
        self.draw_neural_signals()
        self.draw_destroy_particles()
        self.draw_special_effects()
        self.draw_ui_overlay()
        
        # Мини-волна
        self.draw_mini_wave()
        
        # Обновляем информацию
        pulse_val = 50 + 30 * math.sin(self.time_offset)
        self.lbl_pulse.config(text=f"Пульс: {pulse_val:.1f} bpm")
        
        level_val = 30 + 20 * math.sin(self.time_offset * 0.7 + 1)
        self.lbl_level.config(text=f"Уровень: {level_val:.1f}%")
        
        self.cam_info.config(
            text=f"Камера: {int(self.camera_x)}, {int(self.camera_y)}\nМасштаб: {self.camera_zoom:.1f}x"
        )
        
        self.counters.config(
            text=f"Точек: {len(self.points)}\nЛиний: {len(self.lines)}"
        )
        
        load_width = 50 + 150 * abs(math.sin(self.time_offset * 0.3))
        self.loading_bar.coords(self.loading_rect, 0, 0, load_width, 4)
        
        if int(self.time_offset * 10) % 100 < 95:
            self.lbl_net.config(text="Сеть: OK", fg="#2ea043")
        else:
            self.lbl_net.config(text="Сеть: ПАКЕТЫ", fg="#f0883e")
        
        self.root.after(int(self.frame_time * 1000), self.animate)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

# Запуск
if __name__ == "__main__":
    root = tk.Tk()
    app = AbstractDashboard(root)
    root.mainloop()