<div align="center">

# 🧠 NeoBrain Launcher

![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=22&duration=3000&pause=1000&color=00D4FF&center=true&vCenter=true&width=600&lines=AI-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D1%8B+%D0%B2+%D0%BE%D0%B4%D0%BD%D0%BE%D0%BC+%D0%BE%D0%BA%D0%BD%D0%B5;Python+%2B+Ollama+%2B+PySide6;%D0%9B%D0%BE%D0%BA%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9+AI-%D1%87%D0%B0%D1%82)

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-yellow)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

</div>

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-yellow)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

**NeoBrain Launcher** — центральная панель управления для запуска всех проектов NeoBrain в одном окне.  
Включает NeoBrain AI Chat, NeoReceipt, NeoSpace OS и другие утилиты.

---

## 📥 Скачать

**Последняя версия:** [**NeoLauncher v2.0.0**](https://github.com/Sbeuvadyarik67/NeoLauncher-/releases/latest)

1. Скачай `NeoLauncher_v2.0.zip`
2. Распакуй в любую папку
3. Запусти `NeoLauncher.exe`

> **Требования:** [Python 3.10+](https://www.python.org/downloads/) и [Ollama](https://ollama.com/) — для NeoBrain AI.

---

## 📸 Скриншот

![NeoBrain Launcher](https://github.com/user-attachments/assets/4b336725-26f3-4757-a9f5-ba946d54c279)

*4 проекта в одном окне — NeoBrain, NeoSpace OS, Why Does This Exist?, NeoReceipt.*

---

## ✨ Особенности

- 🚀 Быстрый запуск проектов одним кликом
- 🎨 10 тем и 5 стилей интерфейса
- 🧠 NeoBrain AI — локальный чат с персонажами и потоковым режимом
- 📄 NeoReceipt — генератор чеков с живым предпросмотром
- 🖥️ NeoSpace OS — виртуальная среда для экспериментов
- 🔄 Exe не надо пересобирать при обновлении `.py`-файлов

---

## 🚀 Установка

### Для пользователей

Скачай готовый архив со страницы [**Releases**](https://github.com/Sbeuvadyarik67/NeoLauncher-/releases/latest) — распакуй — запусти `NeoLauncher.exe`.

### Для разработчиков

```bash
git clone https://github.com/Sbeuvadyarik67/NeoLauncher-.git
cd NeoLauncher-
pip install -r requirements.txt
python launcher.py
```

### Сборка .exe

```bash
pip install pyinstaller
pyinstaller NeoLauncher.spec
```

Готовый exe — в папке `dist/`.

---

## 📂 Структура

```
NeoLauncher/
├── launcher.py          # Лаунчер
├── manifest.json        # Список проектов
├── icon.ico / icon.png  # Иконки
├── requirements.txt     # Зависимости
└── projects/
    ├── neobrain.py      # 🧠 NeoBrain AI Chat
    ├── neoreceipt.py    # 📄 NeoReceipt
    ├── neospace.py      # 🖥️ NeoSpace OS
    └── whydoes.py       # 🌀 Why Does This Exist?
```

---

## 🧠 NeoBrain AI Chat v7.4

Локальный AI-чат с персонажами.

**Возможности:**

- 🎭 Персонажи с именем, полом, характером (с учётом рода: он/она)
- ⚡ Потоковый режим (можно отключить)
- ⏹ Кнопка остановки генерации
- 🌐 Русский / English
- 🎨 10 тем: Неон, Тёмная, Ночная, Киберпанк, Фиолетовая, Светлая, Розовая, Морская, Мятная, Кремовая
- 💅 5 стилей: По умолчанию, Neon, Claude, Glass, Terminal
- ✨ Плавная смена темы
- 🔒 Работает локально через Ollama

**Первый запуск:**

```bash
ollama pull llama3.2:3b
```

---

## 📄 NeoReceipt 2.0

Генератор чеков с Live Preview.

- 📊 Мульти-товарные чеки
- 👁️ Живой предпросмотр
- 💾 Сохранение шаблонов
- 🔍 Поиск по истории
- 🎨 Выбор стиля оформления

---

## 🖥️ NeoSpace OS

Виртуальная среда для экспериментов.

- 🚀 Запуск виртуальных пространств
- 🎨 Кастомизация окружения
- 🧪 Экспериментальные модули

---

## ❓ FAQ

**Лаунчер пишет «Нет проектов»?**  
Проверь, что папка `projects/` и файл `manifest.json` лежат **рядом** с `NeoLauncher.exe`.

**Нужен ли интернет для NeoBrain?**  
Нет, если модель уже скачана в Ollama. Первый раз: `ollama pull llama3.2:3b`.

**Как обновить проект?**  
Замени `.py`-файл в `projects/`. Exe пересобирать **не нужно**.

---

## 🛠️ Технологии

Python 3.10+ · PySide6 · Tkinter · Ollama · ReportLab · PyInstaller

---

## 📬 Контакты

- **VK:** [vk.ru/v_rusich007](https://vk.ru/v_rusich007)
- **Telegram:** [t.me/sbeuvadyarik](https://t.me/sbeuvadyarik)
- **Gmail:** vvadya041@gmail.com

---

## 📜 Лицензия

MIT License © 2026 Sbeuvadyarik67

**Сделано с ❤️ и 🧠**
