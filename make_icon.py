from PIL import Image, ImageDraw, ImageFont

# Создаем изображение 256x256
img = Image.new('RGBA', (256, 256), (5, 5, 16, 255))
draw = ImageDraw.Draw(img)

# Пытаемся загрузить шрифт
try:
    font = ImageFont.truetype("arialbd.ttf", 180)
except:
    font = ImageFont.load_default()

# Буква N (неоновая - розово-фиолетовая)
draw.text((30, 10), "N", fill=(255, 68, 255, 255), font=font)
draw.text((28, 8), "N", fill=(255, 150, 255, 120), font=font)  # блик

# Буква L (светло-синяя)
draw.text((130, 10), "L", fill=(107, 207, 255, 255), font=font)
draw.text((128, 8), "L", fill=(180, 235, 255, 120), font=font)  # блик

# Сохраняем
img.save('icon.png')
print("✅ icon.png создан!")

# Конвертируем в ICO
img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
print("✅ icon.ico создан!")