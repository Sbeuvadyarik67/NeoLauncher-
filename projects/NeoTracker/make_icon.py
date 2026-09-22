"""
NeoTracker — генерация иконки приложения.

Создаёт .ico файл с буквами "NT":
- N — розовая
- T — голубая
- Фон — тёмный
"""

from PIL import Image, ImageDraw, ImageFont
import os


# ============================================================
# НАСТРОЙКИ
# ============================================================

SIZE = 256  # базовый размер (стандарт для .ico — 256×256)

BG = (13, 17, 23)          # #0d1117 — тёмный фон
PINK = (255, 45, 138)      # #ff2d8a — розовый N
BLUE = (88, 166, 255)      # #58a6ff — голубой T

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "assets", "icon.ico")

# Создаём папку assets
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)


# ============================================================
# ГЕНЕРАЦИЯ
# ============================================================

def make_icon():
    """Создаёт иконку NT."""

    # Создаём изображение с прозрачным фоном
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Рисуем скруглённый квадрат (фон)
    radius = 48
    draw.rounded_rectangle(
        [(0, 0), (SIZE, SIZE)],
        radius=radius,
        fill=BG,
    )

    # ---- Подбираем шрифт ----
    font = None
    font_candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",   # Segoe UI Bold
        "C:/Windows/Fonts/arialbd.ttf",    # Arial Bold
        "C:/Windows/Fonts/tahomabd.ttf",   # Tahoma Bold
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, 150)
                break
            except Exception:
                continue

    if font is None:
        font = ImageFont.load_default()

    # ---- Буква N (розовая) ----
    n_text = "N"
    n_bbox = draw.textbbox((0, 0), n_text, font=font)
    n_width = n_bbox[2] - n_bbox[0]
    n_height = n_bbox[3] - n_bbox[1]

    n_x = 30
    n_y = (SIZE - n_height) // 2 - n_bbox[1]

    draw.text((n_x, n_y), n_text, fill=PINK, font=font)

    # ---- Буква T (голубая) ----
    t_text = "T"
    t_bbox = draw.textbbox((0, 0), t_text, font=font)
    t_width = t_bbox[2] - t_bbox[0]
    t_height = t_bbox[3] - t_bbox[1]

    t_x = n_x + n_width + 10
    t_y = (SIZE - t_height) // 2 - t_bbox[1]

    draw.text((t_x, t_y), t_text, fill=BLUE, font=font)

    # ---- Сохраняем как .ico ----
    # ICO должен содержать несколько размеров
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(OUTPUT_PATH, format="ICO", sizes=sizes)

    # Также сохраним PNG-версию — пригодится для Kwork/README
    png_path = os.path.join(BASE_DIR, "assets", "icon.png")
    img.save(png_path, format="PNG")

    print(f"OK: иконка сохранена:")
    print(f"  ICO: {OUTPUT_PATH}")
    print(f"  PNG: {png_path}")


if __name__ == "__main__":
    make_icon()