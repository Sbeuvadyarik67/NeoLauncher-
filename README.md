<div align="center">

# 🧠 NeoBrain Launcher

![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=22&duration=3000&pause=1000&color=00D4FF&center=true&vCenter=true&width=600&lines=AI-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D1%8B+%D0%B2+%D0%BE%D0%B4%D0%BD%D0%BE%D0%BC+%D0%BE%D0%BA%D0%BD%D0%B5;Python+%2B+Ollama+%2B+PySide6;%D0%9B%D0%BE%D0%BA%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9+AI-%D1%87%D0%B0%D1%82)

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-yellow)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

</div>

![Views](https://dynamic-repo-badges.vercel.app/svg/count/7/Repository%20Views/NeoLauncher-)

![GitHub Streak](https://streak-stats.demolab.com?user=Sbeuvadyarik67&theme=dark&hide_border=true)

**NeoBrain Launcher** — центральная панель управления для запуска всех проектов NeoBrain в одном окне.  
Включает NeoBrain AI Chat, NeoReceipt, NeoSpace OS и другие утилиты.

---

## 📸 Скриншот

<img width="1916" height="1040" alt="image" src="https://github.com/user-attachments/assets/40024b37-1401-414f-95cd-9d8f26efc9e3" />


*5 проектов в одном окне — NeoBrain, Brain Clicker, NeoSpace OS, Why Does This Exist?, NeoReceipt.*

---

## 📥 Скачать

**Последняя версия:** [**NeoLauncher v2.1.0**](https://github.com/Sbeuvadyarik67/NeoLauncher-/releases/latest)

1. Скачай `NeoLauncher_v2.1.0.zip`
2. Распакуй в любую папку
3. Запусти `NeoLauncher.exe`

> **Требования:** [Python 3.10+](https://www.python.org/downloads/) и [Ollama](https://ollama.com/) — для NeoBrain AI.

---

## ✨ Особенности

- 🚀 Быстрый запуск проектов одним кликом
- 🎨 10 тем и 5 стилей интерфейса
- 🧠 NeoBrain AI — локальный чат с персонажами и потоковым режимом
- 📄 NeoReceipt — генератор чеков с живым предпросмотром
- 🖥️ NeoSpace OS — виртуальная среда для экспериментов
- 🔄 Exe не надо пересобирать при обновлении `.py`-файлов
- 🎮 Brain Clicker — кликер с мозгами, тенями и подарками

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
├── launcher.py              # Лаунчер
├── manifest.json            # Список проектов
├── icon.ico / icon.png      # Иконки
├── requirements.txt         # Зависимости
└── projects/
    ├── neobrain.py          # 🧠 NeoBrain AI Chat
    ├── neoreceipt.py        # 📄 NeoReceipt
    ├── neospace.py          # 🖥️ NeoSpace OS
    ├── whydoes.py           # 🌀 Why Does This Exist?
    └── brain-clicker/       # 🎮 Brain Clicker
        ├── index.html       # Игра (HTML)
        ├── style.css        # Стили
        └── script.js        # Логика
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


## 🎮 Brain Clicker

Кликер с мозгами. Кликай → копи → лови тени → собирай подарки.

<img width="1280" height="623" alt="Brain Clicker" src="https://github.com/user-attachments/assets/f7be1140-8def-4982-b653-7f752b029b31" />


- 🧠 **3 фигуры тени** — кто они? Найди сам 👀
- 🎁 **Уникальные подарки** от каждой фигуры
- 🤫 **Скрытая механика** — есть шанс получить кое-что особенное (1% удачи)
- 💤 **Оффлайн-прогресс** — работаю, пока тебя нет
- 🌙 **Возвращайся** — и узнаешь, что накопилось

**Как играть:**

1. Открой лаунчер → `Brain Clicker` → `▶ ЗАПУСТИТЬ`
2. Кликай по мозгу 🧠
3. Жди тень — раз в 30 минут
4. Найди все 3 фигуры
5. Проверь, что даёт каждая

*Есть один сюрприз, который ты не ожидаешь 🏆*

## ❓ FAQ

**Лаунчер пишет «Нет проектов»?**  
Проверь, что папка `projects/` и файл `manifest.json` лежат **рядом** с `NeoLauncher.exe`.

**Нужен ли интернет для NeoBrain?**  
Нет, если модель уже скачана в Ollama. Первый раз: `ollama pull llama3.2:3b`.

**Как обновить проект?**  
Замени `.py`-файл в `projects/`. Exe пересобирать **не нужно**.

**Как запустить Brain Clicker?**  
Через лаунчер: открой `NeoLauncher.exe` → карточка `Brain Clicker` → `▶ ЗАПУСТИТЬ`.  
Игра откроется в браузере (HTML + JS).

---

## 🛠️ Технологии

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PySide6-41CD52?style=for-the-badge&logo=qt&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white" />
  <img src="https://img.shields.io/badge/Tkinter-FF6F00?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/ReportLab-FF0000?style=for-the-badge&logo=adobe-acrobat-reader&logoColor=white" />
  <img src="https://img.shields.io/badge/PyInstaller-FFD43B?style=for-the-badge&logo=python&logoColor=black" />
</p>

---



Если проект полезен:

- ⭐ Поставь **звезду** на GitHub — это мотивирует!
- 🐛 Нашёл баг? [Открой Issue](https://github.com/Sbeuvadyarik67/NeoLauncher-/issues/new/choose)
- 💡 Есть идея? [Предложи фичу](https://github.com/Sbeuvadyarik67/NeoLauncher-/issues/new/choose)

---

## 📬 Контакты

- **VK:** [vk.ru/v_rusich007](https://vk.ru/v_rusich007)
- **Telegram:** [t.me/sbeuvadyarik](https://t.me/sbeuvadyarik)
- **Gmail:** vvadya041@gmail.com

---

## 📜 Лицензия

MIT License © 2026 Sbeuvadyarik67

**Сделано с ❤️ и 🧠**
