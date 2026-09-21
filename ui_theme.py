"""
NeoLauncher — визуальная тема.

Концепция: «Glass Tiles» — тёмный фон с мягкими цветными пятнами,
стеклянные карточки с градиентом и бликом сверху.
"""

import tkinter as tk
import math


# ============================================================
# ПАЛИТРА
# ============================================================

COLORS = {
    # ---- Фон ----
    "bg":           "#08080e",   # почти чёрный
    "bg_spot_1":    "#1a0a2a",   # пятно — пурпур
    "bg_spot_2":    "#0a1a2a",   # пятно — циан
    "bg_spot_3":    "#1a0a1a",   # пятно — розовый

    # ---- Карточки ----
    "card_top":     "#1a1a26",   # карточка сверху
    "card_bottom":  "#0e0e16",   # карточка снизу
    "card_active":  "#1f1f2e",   # активная — чуть светлее
    "card_shadow":  "#04040a",   # тонкая тень снизу (2px)

    "border_dim":   "#2a2a3a",   # обычная обводка
    "border_hover": "#3a3a4a",   # при наведении

    # ---- Текст ----
    "text":         "#e8e8f0",   # основной
    "muted":        "#6a6a7a",   # второстепенный
    "dim":          "#3a3a4a",   # совсем тусклый

    # ---- Акценты ----
    "accent_pink":  "#ff2d8a",
    "accent_cyan":  "#00d4ff",
    "accent_purple":"#8b5cf6",
    "accent_white": "#ffffff",

    # ---- Служебные ----
    "success":      "#10b981",
    "error":        "#ff2d8a",
    "separator":    "#1a1a26",
}


# ============================================================
# ХЕЛПЕРЫ
# ============================================================

def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _lerp(a, b, t):
    return a + (b - a) * t


def blend(c1, c2, t):
    """Смешивает два цвета. t=0 → c1, t=1 → c2."""
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    r = int(_lerp(r1, r2, t))
    g = int(_lerp(g1, g2, t))
    b = int(_lerp(b1, b2, t))
    return f"#{r:02x}{g:02x}{b:02x}"


# ============================================================
# ФОН — цветные пятна + виньетка
# ============================================================

def draw_glass_background(canvas, width, height):
    """
    Рисует фон: тёмная база + мягкие цветные пятна + виньетка.
    """
    canvas.delete("all")

    bg = COLORS["bg"]

    # ---- База ----
    canvas.create_rectangle(0, 0, width, height, fill=bg, outline=bg)

    # ---- Пятна ----
    spots = [
        # (cx_ratio, cy_ratio, radius_ratio, color)
        (0.15, 0.25, 0.45, COLORS["bg_spot_1"]),  # левое верхнее — пурпур
        (0.85, 0.75, 0.50, COLORS["bg_spot_2"]),  # правое нижнее — циан
        (0.50, 0.05, 0.35, COLORS["bg_spot_3"]),  # верх центр — розовое
    ]

    for cx_r, cy_r, radius_r, color in spots:
        cx = int(width * cx_r)
        cy = int(height * cy_r)
        radius = int(max(width, height) * radius_r)

        # Плавное «растворение» пятна — несколько кругов от края к центру
        steps = 25
        for i in range(steps):
            t = i / (steps - 1)
            # от прозрачного (bg) к цвету
            cur_color = blend(bg, color, t)
            r = int(radius * (1 - t * 0.85))
            if r <= 0:
                continue
            canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=cur_color, outline=cur_color
            )

    # ---- Виньетка (затемнение по краям) ----
    # Рисуем тёмные полосы по периметру
    vignette_steps = 12
    for i in range(vignette_steps):
        t = i / vignette_steps
        alpha_color = blend("#000000", bg, 1 - t)
        thickness = int(min(width, height) * 0.05)

        # верх
        canvas.create_rectangle(
            0, 0, width, int(thickness * (1 - t)),
            fill=alpha_color, outline=alpha_color
        )
        # низ
        canvas.create_rectangle(
            0, height - int(thickness * (1 - t)), width, height,
            fill=alpha_color, outline=alpha_color
        )
        # лево
        canvas.create_rectangle(
            0, 0, int(thickness * (1 - t)), height,
            fill=alpha_color, outline=alpha_color
        )
        # право
        canvas.create_rectangle(
            width - int(thickness * (1 - t)), 0, width, height,
            fill=alpha_color, outline=alpha_color
        )


# ============================================================
# СКРУГЛЁННЫЙ ПРЯМОУГОЛЬНИК
# ============================================================

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=12, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1,
        x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2,
        x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius,
        x1, y1 + radius, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)