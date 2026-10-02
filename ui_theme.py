"""
ui_theme — палитры и фоны для NeoBrain Launcher.
Две темы: "neon" (тёмное стекло) и "claude" (тёплый белый).

API совместимо с текущим launcher.py:
    from ui_theme import THEMES, get_theme, draw_glass_background
"""

# ─────────────────────────────────────────────
# NEON
# ─────────────────────────────────────────────
NEON = {
    "bg":             "#0A0A1A",
    "bg2":            "#12122A",
    "card_top":       "#14142B",
    "card_active":    "#1E1E3F",
    "text":           "#E8E8F0",
    "muted":          "#8888AA",
    "dim":            "#555577",
    "accent_pink":    "#FF3E9D",
    "accent_cyan":    "#3EFFFF",
    "accent_purple":  "#9B3EFF",
    "success":        "#3EFF8B",
    "error":          "#FF4E5E",
    "separator":      "#2A2A4A",
    "border_dim":     "#2A2A4A",
    "border_hover":   "#6E6EFF",
    "border_active":  "#FF3E9D",
    "topbar_bg":      "#0A0A1A",
    "bottom_fg":      "#3A3A55",
}

# ─────────────────────────────────────────────
# CLAUDE
# ─────────────────────────────────────────────
CLAUDE = {
    "bg":             "#FAF9F7",
    "bg2":            "#F3F0EB",
    "card_top":       "#FFFFFF",
    "card_active":    "#F5F0EB",
    "text":           "#1A1A1A",
    "muted":          "#6B6B6B",
    "dim":            "#A0A0A0",
    "accent_pink":    "#D97757",
    "accent_cyan":    "#5B8DEF",
    "accent_purple":  "#9B6B9E",
    "success":        "#4A7C59",
    "error":          "#C75450",
    "separator":      "#E0DCD5",
    "border_dim":     "#E5E0D8",
    "border_hover":   "#D97757",
    "border_active":  "#D97757",
    "topbar_bg":      "#FAF9F7",
    "bottom_fg":      "#B0ABA3",
}

# ─────────────────────────────────────────────
# API
# ─────────────────────────────────────────────

THEMES = {
    "neon": NEON,
    "claude": CLAUDE,
}

_current_theme = "neon"


def get_theme():
    """Вернуть имя текущей темы."""
    return _current_theme


def set_theme(name):
    """Установить текущую тему (для совместимости)."""
    global _current_theme
    if name in THEMES:
        _current_theme = name


# ─────────────────────────────────────────────
# ФОН
# ─────────────────────────────────────────────

def draw_glass_background(canvas, w, h, theme_name="neon"):
    """Рисует фон в зависимости от темы."""
    canvas.delete("bg")

    if theme_name == "claude":
        _draw_claude_bg(canvas, w, h)
    else:
        _draw_neon_bg(canvas, w, h)


def _draw_neon_bg(canvas, w, h):
    steps = 60
    for i in range(steps):
        t = i / steps
        r = int(10 + t * 8)
        g = int(10 + t * 22)
        b = int(26 + t * 10)
        color = f"#{r:02x}{g:02x}{b:02x}"
        y0 = int(i * h / steps)
        y1 = int((i + 1) * h / steps) + 1
        canvas.create_rectangle(0, y0, w, y1, fill=color, outline="", tags="bg")

    for cx, cy, rad, col in [
        (w * 0.2, h * 0.3, 280, "#FF3E9D"),
        (w * 0.8, h * 0.7, 300, "#3E9DFF"),
        (w * 0.5, h * 0.5, 200, "#9B3EFF"),
    ]:
        for r in range(int(rad), 0, -12):
            canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=col, outline="", tags="bg"
            )
    canvas.lower("bg")


def _draw_claude_bg(canvas, w, h):
    steps = 60
    for i in range(steps):
        t = i / steps
        r = int(250 - t * 5)
        g = int(249 - t * 7)
        b = int(247 - t * 12)
        color = f"#{r:02x}{g:02x}{b:02x}"
        y0 = int(i * h / steps)
        y1 = int((i + 1) * h / steps) + 1
        canvas.create_rectangle(0, y0, w, y1, fill=color, outline="", tags="bg")

    for cx, cy, rad, col in [
        (w * 0.15, h * 0.2, 350, "#F5EDE3"),
        (w * 0.85, h * 0.8, 300, "#F0E8DD"),
        (w * 0.5, h * 0.5, 200, "#FAF5EE"),
    ]:
        for r in range(int(rad), 0, -12):
            canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=col, outline="", tags="bg"
            )
    canvas.lower("bg")