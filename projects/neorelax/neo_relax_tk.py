import tkinter as tk
import math
import random

# ============================================================
# НАСТРОЙКИ
# ============================================================
WIDTH, HEIGHT = 1200, 800
root = tk.Tk()
root.title("🏛️ Неоновый комплекс")
root.geometry(f"{WIDTH}x{HEIGHT}")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#050510", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# ============================================================
# ПАЛИТРА
# ============================================================
NEON = [
    "#ff2d55", "#00ff87", "#6c5ce7",
    "#fdcb6e", "#00cec9", "#fd79a8",
    "#a29bfe", "#ffeaa7", "#55efc4",
    "#ff7675", "#74b9ff", "#fdcb6e"
]
WHITE = "#ffffff"
DARK = "#0a0a1a"

# ============================================================
# ПАРАМЕТРЫ (ОГРОМНЫЙ МИР)
# ============================================================
world_size = 800
half = world_size // 2
points = []

player_x, player_y, player_z = 0, 0, -200
angle_x, angle_y = 0.05, 0
zoom = 1.0
speed = 6.0
fullscreen = False

last_mx, last_my = 0, 0

# ============================================================
# СОЗДАНИЕ ОГРОМНОГО КОМПЛЕКСА
# ============================================================
def create_complex():
    complex_points = []
    step = 4  # Плотность точек
    spacing = 8  # Шаг для крупных форм

    # ====================
    # ПОЛ (сетка с узором)
    # ====================
    for i in range(-half, half, step):
        for j in range(-half, half, step):
            color = NEON[(i + j) % len(NEON)]
            size = random.uniform(1.5, 3)
            complex_points.append({"x": i, "y": -half, "z": j, "color": color, "size": size})

    # ====================
    # ПОТОЛОК (звёздный купол)
    # ====================
    for i in range(-half, half, step * 2):
        for j in range(-half, half, step * 2):
            color = random.choice(NEON)
            size = random.uniform(1, 2.5)
            complex_points.append({"x": i, "y": half, "z": j, "color": color, "size": size})

    # ====================
    # ОСНОВНЫЕ СТЕНЫ (с колоннами)
    # ====================
    for side in [-1, 1]:
        for i in range(-half, half, step):
            color = NEON[abs(i) % len(NEON)]
            # Стена по X
            complex_points.append({"x": side * half, "y": i, "z": 0, "color": color, "size": 2.5})
            # Стена по Z
            complex_points.append({"x": 0, "y": i, "z": side * half, "color": color, "size": 2.5})

            # Колонны (через каждые 40 единиц)
            if i % 40 == 0:
                for k in range(-8, 9):
                    complex_points.append({
                        "x": side * half,
                        "y": i + k,
                        "z": 0,
                        "color": WHITE,
                        "size": 4.5
                    })
                    complex_points.append({
                        "x": 0,
                        "y": i + k,
                        "z": side * half,
                        "color": WHITE,
                        "size": 4.5
                    })

    # ====================
    # ВНУТРЕННИЕ СТЕНЫ (коридоры)
    # ====================
    for offset in [-300, 300]:
        for side in [-1, 1]:
            for i in range(-200, 200, step):
                x_pos = side * offset
                z_pos = i
                color = NEON[(i + offset) % len(NEON)]
                complex_points.append({
                    "x": x_pos,
                    "y": i,
                    "z": z_pos,
                    "color": color,
                    "size": 2
                })

    # ====================
    # АРКИ (входы в залы)
    # ====================
    for center in [-200, 200]:
        for z_center in [-200, 200]:
            for i in range(-50, 51, step):
                for j in range(0, 60, step):
                    x = center + i
                    z = z_center
                    y = -half + j
                    if j > 30:
                        y = -half + 30 + (j - 30) * 0.3
                    complex_points.append({
                        "x": x, "y": y, "z": z,
                        "color": "#ff2d55",
                        "size": random.uniform(2, 3.5)
                    })

    # ====================
    # ЛЕСТНИЦА (в центре)
    # ====================
    for step_h in range(0, 60, 5):
        for i in range(-30, 31, step):
            y_pos = -half + step_h
            z_pos = i
            x_pos = step_h * 0.8 - 40
            complex_points.append({
                "x": x_pos,
                "y": y_pos,
                "z": z_pos,
                "color": "#00ff87",
                "size": random.uniform(2, 4)
            })

    # ====================
    # НИШИ (светящиеся проёмы)
    # ====================
    for side in [-1, 1]:
        for n_x in [-150, 150]:
            for n_y in range(-30, 40, step):
                complex_points.append({
                    "x": side * half,
                    "y": n_y,
                    "z": n_x,
                    "color": "#74b9ff",
                    "size": random.uniform(2, 4)
                })

    # ====================
    # КОЛОННАДА (в центре)
    # ====================
    for i in range(-100, 101, 30):
        for side in [-1, 1]:
            for k in range(-20, 21, 4):
                complex_points.append({
                    "x": i,
                    "y": k,
                    "z": side * 50,
                    "color": WHITE,
                    "size": random.uniform(3, 5)
                })

    return complex_points

points = create_complex()

# ============================================================
# ОТРИСОВКА (оптимизированная)
# ============================================================
def draw():
    canvas.delete("all")
    cx = WIDTH // 2
    cy = HEIGHT // 2

    # Сортировка по глубине (один раз)
    sorted_points = sorted(points, key=lambda p: p["z"], reverse=True)

    for p in sorted_points:
        dx = p["x"] - player_x
        dy = p["y"] - player_y
        dz = p["z"] - player_z

        # Если точка слишком далеко — пропускаем (оптимизация)
        if abs(dx) > 800 or abs(dy) > 600 or dz < -800:
            continue

        # Поворот камеры
        cos_x = math.cos(angle_x)
        sin_x = math.sin(angle_x)
        cos_y = math.cos(angle_y)
        sin_y = math.sin(angle_y)

        y1 = dy * cos_x - dz * sin_x
        z1 = dy * sin_x + dz * cos_x
        x1 = dx

        x2 = x1 * cos_y + z1 * sin_y
        z2 = -x1 * sin_y + z1 * cos_y
        y2 = y1

        if z2 > -10:
            scale = 300 / (300 + z2 * 0.25) * zoom
            sx = x2 * scale + cx
            sy = y2 * scale + cy
            size = p["size"] * scale * 0.8

            if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:
                canvas.create_oval(
                    sx - size, sy - size,
                    sx + size, sy + size,
                    fill=p["color"], outline=""
                )

    root.after(8, draw)  # 125 FPS

# ============================================================
# ДВИЖЕНИЕ
# ============================================================
def move_player(dx, dy, dz):
    global player_x, player_y, player_z, points

    forward_x = math.sin(angle_y) * dx
    forward_z = math.cos(angle_y) * dx

    side_x = math.cos(angle_y) * dz
    side_z = -math.sin(angle_y) * dz

    new_x = player_x + forward_x + side_x
    new_y = player_y + dy
    new_z = player_z + forward_z + side_z

    # Ограничение (не выходить за пределы)
    if abs(new_x) < half - 50 and abs(new_z) < half - 50:
        player_x, player_y, player_z = new_x, new_y, new_z

    # Мир меняется за спиной
    for p in points:
        dz_to_player = p["z"] - player_z
        if dz_to_player < -100:
            p["x"] += random.uniform(-15, 15)
            p["y"] += random.uniform(-15, 15)
            p["z"] += random.uniform(200, 350)
            p["color"] = random.choice(NEON)
            p["size"] = random.uniform(1.5, 4)

# ============================================================
# УПРАВЛЕНИЕ
# ============================================================
def on_key(event):
    global speed, fullscreen
    step = speed * 0.3

    if event.keysym == "w":
        move_player(step, 0, 0)
    elif event.keysym == "s":
        move_player(-step, 0, 0)
    elif event.keysym == "a":
        move_player(0, 0, -step)
    elif event.keysym == "d":
        move_player(0, 0, step)
    elif event.keysym == "q":
        move_player(0, -step, 0)
    elif event.keysym == "e":
        move_player(0, step, 0)
    elif event.keysym == "r":
        speed = min(speed + 0.5, 10.0)
    elif event.keysym == "f":
        speed = max(speed - 0.5, 1.0)
    elif event.keysym == "F11":
        fullscreen = not fullscreen
        root.attributes("-fullscreen", fullscreen)

def on_mouse_move(event):
    global angle_x, angle_y, last_mx, last_my
    dx = event.x - last_mx
    dy = event.y - last_my
    angle_y += dx * 0.002
    angle_x += dy * 0.002
    angle_x = max(-1.3, min(1.3, angle_x))
    last_mx, last_my = event.x, event.y

def on_mouse_enter(event):
    global last_mx, last_my
    last_mx, last_my = event.x, event.y

def on_mousewheel(event):
    global zoom
    zoom *= 1.1 if event.delta > 0 else 0.9
    zoom = max(0.2, min(5.0, zoom))

# ============================================================
# ПРИВЯЗКА
# ============================================================
root.bind("<Key>", on_key)
canvas.bind("<Motion>", on_mouse_move)
canvas.bind("<Enter>", on_mouse_enter)
canvas.bind("<MouseWheel>", on_mousewheel)
canvas.focus_set()

# ============================================================
# ЗАПУСК
# ============================================================
draw()
root.mainloop()