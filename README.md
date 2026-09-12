# 🧠 NeoBrain Launcher

**NeoBrain Launcher** — центральная панель управления для запуска всех проектов NeoBrain в одном окне.  
Включает NeoBrain AI Chat, NeoReceipt, NeoSpace OS и другие утилиты.

---

## 📥 Скачать

**Последняя версия:** [**NeoLauncher v2.0.0**](https://github.com/Sbeuvadyarik67/NeoLauncher-/releases/latest)

1. Скачай `NeoLauncher_v2.0.zip`
2. Распакуй в любую папку
3. Запусти `NeoLauncher.exe`

> **Требования:** [Python 3.10+](https://www.python.org/downloads/) (отметь галочку *Add Python to PATH*) и [Ollama](https://ollama.com/) — для NeoBrain AI.

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
