"""
Игры для NeoSpace OS
"""
import tkinter as tk
import random
import time

# ===================================================
# САПЁР
# ===================================================
class Minesweeper:
    def __init__(self, parent, os_instance):
        self.parent = parent
        self.os = os_instance
        self.rows = 10
        self.cols = 10
        self.mines = 15
        self.buttons = []
        self.mine_positions = set()
        self.revealed = set()
        self.flags = set()
        self.game_over = False
        self.first_click = True
        
        # Получаем цвета из os_instance
        global COLORS
        if hasattr(os_instance, 'COLORS'):
            COLORS = os_instance.COLORS
        else:
            COLORS = {
                "window_bg": "#0a0e1a",
                "bg": "#0a0e1a",
                "bg_light": "#161f3a",
                "fg": "#e0f0ff",
                "fg_secondary": "#88bbdd",
                "accent": "#00d4ff",
                "taskbar": "#0a0e1a",
                "button_close": "#ff6b6b"
            }
        
        self._create_ui()
    
    def _create_ui(self):
        # Информационная панель
        info_frame = tk.Frame(self.parent, bg=COLORS["window_bg"])
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.mines_label = tk.Label(info_frame, text=f"💣 Мин: {self.mines}", 
                                    font=("Segoe UI", 12, "bold"),
                                    fg=COLORS["fg"], bg=COLORS["window_bg"])
        self.mines_label.pack(side="left", padx=10)
        
        self.status_label = tk.Label(info_frame, text="▶️ Кликни на поле", 
                                     font=("Segoe UI", 12),
                                     fg=COLORS["fg_secondary"], bg=COLORS["window_bg"])
        self.status_label.pack(side="right", padx=10)
        
        # Поле
        self.game_frame = tk.Frame(self.parent, bg=COLORS["window_bg"])
        self.game_frame.pack(padx=10, pady=10)
        
        self._create_grid()
    
    def _create_grid(self):
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                btn = tk.Button(self.game_frame, text="", width=3, height=1,
                               font=("Segoe UI", 12, "bold"),
                               bg=COLORS["bg_light"], fg=COLORS["fg"],
                               relief="raised", cursor="hand2")
                btn.grid(row=r, column=c, padx=1, pady=1)
                btn.bind("<Button-1>", lambda e, row=r, col=c: self._left_click(row, col))
                btn.bind("<Button-3>", lambda e, row=r, col=c: self._right_click(row, col))
                row.append(btn)
            self.buttons.append(row)
    
    def _setup_game(self, safe_row, safe_col):
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        # Убираем безопасную клетку и её соседей
        safe_positions = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = safe_row + dr, safe_col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    safe_positions.add((nr, nc))
        
        available = [p for p in positions if p not in safe_positions]
        self.mine_positions = set(random.sample(available, self.mines))
        
        self.revealed.clear()
        self.flags.clear()
        self.game_over = False
        self.first_click = False
        
        self.status_label.config(text="▶️ Игра начата", fg=COLORS["fg_secondary"])
        self.mines_label.config(text=f"💣 Мин: {self.mines - len(self.flags)}")
    
    def _left_click(self, row, col):
        if self.game_over:
            return
        if (row, col) in self.flags:
            return
        if (row, col) in self.revealed:
            return
        
        if self.first_click:
            self._setup_game(row, col)
        
        if (row, col) in self.mine_positions:
            self._game_over(False)
            return
        
        self._reveal(row, col)
        self._check_win()
    
    def _right_click(self, row, col):
        if self.game_over:
            return
        if self.first_click:
            return
        if (row, col) in self.revealed:
            return
        
        if (row, col) in self.flags:
            self.flags.remove((row, col))
            self.buttons[row][col].config(text="", bg=COLORS["bg_light"])
        else:
            self.flags.add((row, col))
            self.buttons[row][col].config(text="🚩", fg="red", bg=COLORS["bg_light"])
        self.mines_label.config(text=f"💣 Мин: {self.mines - len(self.flags)}")
    
    def _reveal(self, row, col):
        if (row, col) in self.revealed:
            return
        if (row, col) in self.mine_positions:
            return
        
        self.revealed.add((row, col))
        count = self._count_mines(row, col)
        
        if count > 0:
            self.buttons[row][col].config(text=str(count), 
                                         bg=COLORS["bg"], relief="sunken")
        else:
            self.buttons[row][col].config(text="", 
                                         bg=COLORS["bg"], relief="sunken")
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if (nr, nc) not in self.revealed and (nr, nc) not in self.mine_positions:
                            self._reveal(nr, nc)
    
    def _count_mines(self, row, col):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if (nr, nc) in self.mine_positions:
                        count += 1
        return count
    
    def _game_over(self, won):
        self.game_over = True
        for r, c in self.mine_positions:
            if (r, c) not in self.revealed and (r, c) not in self.flags:
                self.buttons[r][c].config(text="💣", bg=COLORS["button_close"])
        if won:
            self.status_label.config(text="🎉 Вы выиграли!", fg="green")
        else:
            self.status_label.config(text="💥 Вы проиграли!", fg="red")
    
    def _check_win(self):
        safe_cells = self.rows * self.cols - self.mines
        if len(self.revealed) >= safe_cells:
            self._game_over(True)

# ===================================================
# ЗМЕЙКА
# ===================================================
class Snake:
    def __init__(self, parent, os_instance):
        self.parent = parent
        self.os = os_instance
        self.size = 20
        self.delay = 200
        self.snake = [(8, 8), (7, 8), (6, 8)]
        self.direction = "Right"
        self.food = None
        self.score = 0
        self.game_over = False
        self.running = True
        
        # Получаем цвета из os_instance
        global COLORS
        if hasattr(os_instance, 'COLORS'):
            COLORS = os_instance.COLORS
        else:
            COLORS = {
                "window_bg": "#0a0e1a",
                "bg": "#0a0e1a",
                "bg_light": "#161f3a",
                "fg": "#e0f0ff",
                "fg_secondary": "#88bbdd",
                "accent": "#00d4ff"
            }
        
        self._create_ui()
        self._spawn_food()
        self._update()
        
        self.parent.bind("<KeyPress>", self._on_key)
        self.parent.focus_set()
    
    def _create_ui(self):
        info_frame = tk.Frame(self.parent, bg=COLORS["window_bg"])
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.score_label = tk.Label(info_frame, text=f"🍎 Очки: {self.score}", 
                                    font=("Segoe UI", 14, "bold"),
                                    fg=COLORS["fg"], bg=COLORS["window_bg"])
        self.score_label.pack(side="left", padx=10)
        
        self.status_label = tk.Label(info_frame, text="⬆⬇⬅➡ Управляй стрелками", 
                                     font=("Segoe UI", 11),
                                     fg=COLORS["fg_secondary"], bg=COLORS["window_bg"])
        self.status_label.pack(side="right", padx=10)
        
        self.canvas = tk.Canvas(self.parent, bg=COLORS["bg"], highlightthickness=1,
                                highlightbackground=COLORS["bg_light"])
        self.canvas.pack(padx=10, pady=10, expand=True, fill="both")
        
        self._draw()
    
    def _draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() if self.canvas.winfo_width() > 0 else 500
        h = self.canvas.winfo_height() if self.canvas.winfo_height() > 0 else 500
        cell_w = w // self.size
        cell_h = h // self.size
        
        for i, (x, y) in enumerate(self.snake):
            color = "#44ff88" if i == 0 else "#22cc66"
            self.canvas.create_rectangle(x * cell_w, y * cell_h,
                                         (x+1) * cell_w, (y+1) * cell_h,
                                         fill=color, outline=COLORS["bg"])
        
        if self.food:
            x, y = self.food
            self.canvas.create_oval(x * cell_w, y * cell_h,
                                    (x+1) * cell_w, (y+1) * cell_h,
                                    fill="#ff4444", outline=COLORS["bg"])
    
    def _spawn_food(self):
        while True:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
    
    def _update(self):
        if not self.running:
            return
        if self.game_over:
            return
        
        head = self.snake[0]
        if self.direction == "Up":
            new_head = (head[0], head[1] - 1)
        elif self.direction == "Down":
            new_head = (head[0], head[1] + 1)
        elif self.direction == "Left":
            new_head = (head[0] - 1, head[1])
        else:
            new_head = (head[0] + 1, head[1])
        
        if new_head[0] < 0 or new_head[0] >= self.size or new_head[1] < 0 or new_head[1] >= self.size:
            self._game_over()
            return
        
        if new_head in self.snake[:-1]:
            self._game_over()
            return
        
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.score += 1
            self.score_label.config(text=f"🍎 Очки: {self.score}")
            self._spawn_food()
            if self.delay > 80:
                self.delay -= 5
        else:
            self.snake.pop()
        
        self._draw()
        self.parent.after(self.delay, self._update)
    
    def _on_key(self, e):
        key = e.keysym
        if key in ["Up", "Down", "Left", "Right"]:
            opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
            if key != opposites.get(self.direction, ""):
                self.direction = key
    
    def _game_over(self):
        self.game_over = True
        self.status_label.config(text="💀 Игра окончена! Нажми R для рестарта", fg="red")
        self.running = False
        self.parent.bind("<Key-r>", lambda e: self._restart())
        self.parent.bind("<Key-R>", lambda e: self._restart())
    
    def _restart(self):
        self.snake = [(8, 8), (7, 8), (6, 8)]
        self.direction = "Right"
        self.score = 0
        self.game_over = False
        self.running = True
        self.delay = 200
        self.score_label.config(text=f"🍎 Очки: {self.score}")
        self.status_label.config(text="⬆⬇⬅➡ Управляй стрелками", fg=COLORS["fg_secondary"])
        self._spawn_food()
        self._update()

# ===================================================
# ЛОВЕЦ ПРЕДМЕТОВ
# ===================================================
class Catcher:
    def __init__(self, parent, os_instance):
        self.parent = parent
        self.os = os_instance
        
        # Получаем цвета из os_instance
        global COLORS
        if hasattr(os_instance, 'COLORS'):
            COLORS = os_instance.COLORS
        else:
            COLORS = {
                "window_bg": "#0a0e1a",
                "bg": "#0a0e1a",
                "bg_light": "#161f3a",
                "fg": "#e0f0ff",
                "fg_secondary": "#88bbdd",
                "accent": "#00d4ff"
            }
        
        self.width = 500
        self.height = 500
        self.paddle_width = 80
        self.paddle_height = 15
        self.paddle_x = 250
        self.paddle_y = 470
        self.item_size = 30
        self.items = []
        self.score = 0
        self.lives = 3
        self.running = True
        self.speed = 3
        
        self._create_ui()
        self._spawn_item()
        self._update()
        
        self.parent.bind("<KeyPress-Left>", self._move_left)
        self.parent.bind("<KeyPress-Right>", self._move_right)
        self.parent.focus_set()
    
    def _create_ui(self):
        info_frame = tk.Frame(self.parent, bg=COLORS["window_bg"])
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.score_label = tk.Label(info_frame, text=f"⭐ Очки: {self.score}", 
                                    font=("Segoe UI", 14, "bold"),
                                    fg=COLORS["fg"], bg=COLORS["window_bg"])
        self.score_label.pack(side="left", padx=10)
        
        self.lives_label = tk.Label(info_frame, text=f"❤️ Жизни: {self.lives}", 
                                    font=("Segoe UI", 14, "bold"),
                                    fg=COLORS["fg"], bg=COLORS["window_bg"])
        self.lives_label.pack(side="left", padx=20)
        
        self.status_label = tk.Label(info_frame, text="⬅➡ Управляй стрелками", 
                                     font=("Segoe UI", 11),
                                     fg=COLORS["fg_secondary"], bg=COLORS["window_bg"])
        self.status_label.pack(side="right", padx=10)
        
        self.canvas = tk.Canvas(self.parent, bg=COLORS["bg"], highlightthickness=1,
                                highlightbackground=COLORS["bg_light"])
        self.canvas.pack(padx=10, pady=10, expand=True, fill="both")
        
        self._draw()
    
    def _draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() if self.canvas.winfo_width() > 0 else 500
        h = self.canvas.winfo_height() if self.canvas.winfo_height() > 0 else 500
        
        # Корзинка
        self.canvas.create_rectangle(self.paddle_x - self.paddle_width//2, self.paddle_y,
                                     self.paddle_x + self.paddle_width//2, self.paddle_y + self.paddle_height,
                                     fill=COLORS["accent"], outline=COLORS["accent"])
        
        # Предметы
        for item in self.items:
            x, y, item_type = item
            if item_type == "good":
                color = "#44ff88"
                symbol = "⭐"
            elif item_type == "bad":
                color = "#ff4444"
                symbol = "💥"
            else:
                color = "#ffaa44"
                symbol = "💰"
            
            self.canvas.create_oval(x - self.item_size//2, y - self.item_size//2,
                                    x + self.item_size//2, y + self.item_size//2,
                                    fill=color, outline=COLORS["bg"])
            self.canvas.create_text(x, y, text=symbol, font=("Segoe UI", 14))
    
    def _spawn_item(self):
        if not self.running:
            return
        w = self.canvas.winfo_width() if self.canvas.winfo_width() > 0 else 500
        x = random.randint(self.item_size, w - self.item_size)
        item_type = random.choices(["good", "good", "good", "bad", "bonus"], weights=[40, 30, 20, 8, 2])[0]
        self.items.append([x, 0, item_type])
    
    def _update(self):
        if not self.running:
            return
        
        w = self.canvas.winfo_width() if self.canvas.winfo_width() > 0 else 500
        h = self.canvas.winfo_height() if self.canvas.winfo_height() > 0 else 500
        
        # Двигаем предметы
        for item in self.items[:]:
            item[1] += self.speed
            
            # Проверка столкновения с корзинкой
            if item[1] + self.item_size//2 >= self.paddle_y:
                if self.paddle_x - self.paddle_width//2 < item[0] < self.paddle_x + self.paddle_width//2:
                    # Поймали!
                    if item[2] == "good":
                        self.score += 10
                    elif item[2] == "bonus":
                        self.score += 50
                    else:  # bad
                        self.lives -= 1
                    self.items.remove(item)
                    self._update_labels()
                    continue
                else:
                    # Промах
                    if item[2] == "bad":
                        pass  # Ничего не делаем
                    else:
                        self.lives -= 1
                    self.items.remove(item)
                    self._update_labels()
                    continue
            
            # Предмет упал
            if item[1] > h:
                self.items.remove(item)
                if item[2] != "bad":
                    self.lives -= 1
                    self._update_labels()
                continue
        
        # Проверка жизни
        if self.lives <= 0:
            self._game_over()
            return
        
        # Спавн новых предметов
        if random.random() < 0.02:
            self._spawn_item()
        
        self._draw()
        self.parent.after(30, self._update)
    
    def _move_left(self, e):
        w = self.canvas.winfo_width() if self.canvas.winfo_width() > 0 else 500
        self.paddle_x = max(self.paddle_width//2, self.paddle_x - 20)
    
    def _move_right(self, e):
        w = self.canvas.winfo_width() if self.canvas.winfo_width() > 0 else 500
        self.paddle_x = min(w - self.paddle_width//2, self.paddle_x + 20)
    
    def _update_labels(self):
        self.score_label.config(text=f"⭐ Очки: {self.score}")
        self.lives_label.config(text=f"❤️ Жизни: {self.lives}")
    
    def _game_over(self):
        self.running = False
        self.status_label.config(text="💀 Игра окончена! Нажми R для рестарта", fg="red")
        self.parent.bind("<Key-r>", lambda e: self._restart())
        self.parent.bind("<Key-R>", lambda e: self._restart())
    
    def _restart(self):
        self.paddle_x = 250
        self.items = []
        self.score = 0
        self.lives = 3
        self.running = True
        self.speed = 3
        self._update_labels()
        self.status_label.config(text="⬅➡ Управляй стрелками", fg=COLORS["fg_secondary"])
        self.parent.unbind("<Key-r>")
        self.parent.unbind("<Key-R>")
        self._spawn_item()
        self._update()