import tkinter as tk
from tkinter import messagebox
import random
import time
import os
import pygame


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Сапер")
        self.resizable(False, False)

        self.frames = {}

        for FrameClass in (MainMenu, DifficultySelector, StatisticsScreen):
            frame = FrameClass(self, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("MainMenu")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

        self.update_idletasks()
        width = frame.winfo_reqwidth()
        height = frame.winfo_reqheight()
        self.center_window(width, height)

    def start_game(self, rows, cols, mines):
        game_screen = GameScreen(self, self, rows, cols, mines)
        self.frames["GameScreen"] = game_screen
        game_screen.place(relwidth=1, relheight=1)
        self.show_frame("GameScreen")

    def center_window(self, width, height):

        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=400, height=300)
        self.controller = controller
        self.pack_propagate(False)

        tk.Label(self, text="Сапер:", font=("Arial", 14), justify="center").pack(pady=50)

        tk.Button(self, text="Грати (Вибір складності)", font=("Arial", 12), width=20, command=lambda: controller.show_frame("DifficultySelector")).pack(pady=10)

        tk.Button(self, text="Статистика", font=("Arial", 12), width=20, command=lambda: controller.show_frame("StatisticsScreen")).pack(pady=10)

        tk.Button(self, text="Вийти", font=("Arial", 12), width=20, command=self.quit).pack(pady=10)


class DifficultySelector(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=250, height=260)
        self.controller = controller
        self.pack_propagate(False)

        tk.Label(self, text="Оберіть рівень складності:", font=('Arial', 12)).pack(anchor='w', padx=10, pady=5)

        self.diff_var = tk.StringVar(value="beginner")
        tk.Radiobutton(self, text="Початковий (9x9, 10 мін)", variable=self.diff_var, value="beginner").pack(anchor='w', padx=20)
        tk.Radiobutton(self, text="Просунутий (16x16, 40 мін)", variable=self.diff_var, value="advanced").pack(anchor='w', padx=20)
        tk.Radiobutton(self, text="Кастом", variable=self.diff_var, value="custom", command=lambda: self.toggle_custom(True)).pack(anchor='w', padx=20)

        self.custom_frame = tk.Frame(self)
        tk.Label(self.custom_frame, text="Ширина:").grid(row=0, column=0, padx=5)
        self.entry_cols = tk.Entry(self.custom_frame, width=5)
        self.entry_cols.grid(row=0, column=1)

        tk.Label(self.custom_frame, text="Висота:").grid(row=1, column=0, padx=5)
        self.entry_rows = tk.Entry(self.custom_frame, width=5)
        self.entry_rows.grid(row=1, column=1)

        tk.Label(self.custom_frame, text="Міни:").grid(row=2, column=0, padx=5)
        self.entry_mines = tk.Entry(self.custom_frame, width=5)
        self.entry_mines.grid(row=2, column=1)

        self.toggle_custom()

        tk.Button(self, text="Почати гру", command=self.start_game).pack(pady=10)
        tk.Button(self, text="Меню", command=lambda: self.controller.show_frame("MainMenu")).pack(pady=5)


    def toggle_custom(self, force=False):
        if self.diff_var.get() == "custom" or force:
            self.custom_frame.pack()
        else:
            self.custom_frame.pack_forget()

    def start_game(self):
        diff = self.diff_var.get()
        if diff == "beginner":
            self.controller.start_game(9, 9, 10)
        elif diff == "advanced":
            self.controller.start_game(16, 16, 40)
        else:
            try:
                rows = int(self.entry_rows.get())
                cols = int(self.entry_cols.get())
                mines = int(self.entry_mines.get())
                assert 1 <= rows <= 40 and 1 <= cols <= 40 and 1 <= mines < rows * cols
                self.controller.start_game(rows, cols, mines)
            except:
                messagebox.showerror("Помилка", "Неправильні значення!")


class StatisticsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=450, height=350)
        self.controller = controller
        self.pack_propagate(False)

        tk.Label(self, text="Статистика ігор", font=("Arial", 16)).pack(pady=10)
        self.stats_frame = tk.Frame(self)
        self.stats_frame.pack()

        tk.Button(self, text="Назад", command=lambda: controller.show_frame("MainMenu")).pack(pady=5)

        tk.Button(self, text="Очистити статистику", command=self.clear_stats, bg="#dd5555", fg="white").pack(pady=5)

        self.load_stats()

    def clear_stats(self):
        if messagebox.askyesno("Очистити статистику", "Ви впевнені, що хочете повністю очистити статистику?"):
            with open("stats.txt", "w", encoding="utf-8") as f:
                f.write("")
            messagebox.showinfo("Готово", "Статистику очищено.")
            self.load_stats()

    def load_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        filename = "stats.txt"
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            tk.Label(self.stats_frame, text="Немає збереженої статистики.").pack()
            return

        has_data = False

        with open(filename, "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) == 2:
                    try:
                        level = parts[0]
                        games, wins, total_time, total_moves, best_time, best_moves = map(int, parts[1].split(","))
                        avg_time = total_time // wins if wins else 0
                        avg_moves = total_moves // wins if wins else 0
                        win_rate = round(wins / games * 100, 2) if games else 0
                        stat_text = (
                            f"{level}:\n"
                            f"  Ігор: {games}, Перемог: {wins}, Win%: {win_rate}%\n"
                            f"  При перемогі:\n"
                            f"  Середній час: {avg_time} сек, Найкращий час: {best_time} сек\n"
                            f"  Середні ходи: {avg_moves}, Мін. ходів: {best_moves}\n"
                        )
                        tk.Label(self.stats_frame, text=stat_text, anchor="w", justify="left", font=("Arial", 10)).pack(
                            anchor="w", padx=20, pady=2)
                        has_data = True
                    except Exception:
                        continue
        if not has_data:
            tk.Label(self.stats_frame, text="Немає збереженої статистики.").pack()


class GameScreen(tk.Frame):
    def __init__(self, parent, controller, rows, cols, mines):
        width = max(300, cols * 30)
        height = max(300, rows * 30 + 80)
        super().__init__(parent, width=width, height=height)
        self.controller = controller
        self.pack_propagate(False)

        self.game = Game(self, rows, cols, mines, controller)
        self.game.pack()


class SoundManager:
    @staticmethod
    def play_win_sound():
        pygame.mixer.init()
        pygame.mixer.music.load("zvuk_pobedyi.wav")
        pygame.mixer.music.play()

    @staticmethod
    def play_lose_sound():
        pygame.mixer.init()
        pygame.mixer.music.load("vzryv_saper.wav")
        pygame.mixer.music.play()


class Game(tk.Frame):
    def __init__(self, parent, rows, cols, mines, controller):
        super().__init__(parent)
        self.controller = controller
        self.master = parent
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.buttons = {}
        self.mines_set = set()
        self.flags = set()
        self.revealed = set()
        self.numbers = {}
        self.start_time = None
        self.timer_id = None
        self.moves = 0
        self.first_click_done = False
        self.game_finished = False

        self.create_widgets()


    def create_widgets(self):
        top_frame = tk.Frame(self)
        top_frame.pack()

        self.timer_label = tk.Label(top_frame, text="Час: 0", font=('Arial', 12))
        self.timer_label.pack(side=tk.LEFT, padx=20)

        self.mines_label = tk.Label(top_frame, text=f"Міни: {self.mines}", font=('Arial', 12))
        self.mines_label.pack(side=tk.RIGHT, padx=20)

        self.moves_label = tk.Label(top_frame, text="Ходи: 0", font=('Arial', 12), width=14, anchor="center")
        self.moves_label.pack(side=tk.LEFT, padx=10)

        frame = tk.Frame(self)
        frame.pack()
        for x in range(self.cols):
            for y in range(self.rows):
                btn = tk.Button(frame, width=2, height=1, font=('Arial', 12), bg="#d3d3d3", activebackground="#b0b0b0", relief=tk.RAISED)
                btn.bind("<Button-1>", lambda e, x=x, y=y: self.left_click(x, y))
                btn.bind("<Button-3>", lambda e, x=x, y=y: self.toggle_flag(x, y))
                btn.grid(row=y, column=x)
                self.buttons[(x, y)] = btn

    def start_timer(self):
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Час: {elapsed}")
        self.timer_id = self.after(1000, self.update_timer)

    def place_mines(self, fx, fy):
        self.mines_set.clear()
        forbidden = {(fx, fy)}
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = fx + dx, fy + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    forbidden.add((nx, ny))
        while len(self.mines_set) < self.mines:
            x = random.randint(0, self.cols - 1)
            y = random.randint(0, self.rows - 1)
            if (x, y) not in forbidden:
                self.mines_set.add((x, y))

    def calculate_numbers(self):
        for x in range(self.cols):
            for y in range(self.rows):
                if (x, y) in self.mines_set:
                    self.numbers[(x, y)] = -1
                else:
                    count = sum((nx, ny) in self.mines_set
                                for nx in range(x - 1, x + 2)
                                for ny in range(y - 1, y + 2)
                                if 0 <= nx < self.cols and 0 <= ny < self.rows)
                    self.numbers[(x, y)] = count

    def left_click(self, x, y):
        if not self.first_click_done:
            self.place_mines(x, y)
            self.calculate_numbers()
            self.first_click_done = True
            self.start_timer()
        self.moves += 1
        self.moves_label.config(text=f"Ходи: {self.moves}")

        if (x, y) in self.revealed and self.numbers[(x, y)] > 0:
            self.chord_reveal(x, y)
        else:
            self.reveal(x, y)



    def toggle_flag(self, x, y):
        if (x, y) in self.revealed:
            return
        btn = self.buttons[(x, y)]
        if (x, y) in self.flags:
            btn.config(text="", fg="black")
            self.flags.remove((x, y))
        else:
            btn.config(text="⚑", fg="red")
            self.flags.add((x, y))
        self.moves += 1
        self.moves_label.config(text=f"Ходи: {self.moves}")
        self.mines_label.config(text=f"Міни: {self.mines - len(self.flags)}")

    def chord_reveal(self, x, y):
        flag_count = sum((nx, ny) in self.flags
                         for nx in range(x - 1, x + 2)
                         for ny in range(y - 1, y + 2)
                         if 0 <= nx < self.cols and 0 <= ny < self.rows)
        if flag_count == self.numbers[(x, y)]:
            for nx in range(x - 1, x + 2):
                for ny in range(y - 1, y + 2):
                    if 0 <= nx < self.cols and 0 <= ny < self.rows:
                        if (nx, ny) not in self.flags:
                            self.reveal(nx, ny)

    def reveal(self, x, y):
        if (x, y) in self.revealed or (x, y) in self.flags:
            return

        btn = self.buttons[(x, y)]

        if (x, y) in self.mines_set:
            btn.config(text="*", bg="red")
            if not self.game_finished:
                self.game_finished = True
                self.game_over(False, exploded=(x, y))
            SoundManager.play_lose_sound()
            return
        else:
            count = self.numbers[(x, y)]
            btn.config(text=str(count) if count else "", relief=tk.SUNKEN, state=tk.DISABLED, disabledforeground=self.get_color(count))
            self.revealed.add((x, y))
            if count == 0:
                for nx in range(x - 1, x + 2):
                    for ny in range(y - 1, y + 2):
                        if 0 <= nx < self.cols and 0 <= ny < self.rows:
                            self.reveal(nx, ny)
            if len(self.revealed) == self.rows * self.cols - self.mines and not self.game_finished:
                self.game_finished = True
                self.game_over(True)

    def get_color(self, count):
        colors = ["black", "blue", "green", "red", "purple", "maroon", "turquoise", "gray", "orange"]
        return colors[count] if count < len(colors) else "black"

    def game_over(self, win, exploded=None):
        if self.timer_id:
            self.after_cancel(self.timer_id)

        for (x, y) in self.mines_set:
            if (x, y) == exploded:
                continue
            if (x, y) not in self.flags:
                self.buttons[(x, y)].config(text="*", bg="gray")

        for (x, y) in self.flags:
            if (x, y) not in self.mines_set:
                self.buttons[(x, y)].config(text="✗", bg="yellow")

        for btn in self.buttons.values():
            btn.unbind("<Button-1>")
            btn.unbind("<Button-3>")
            btn.config(state=tk.DISABLED)

        elapsed = int(time.time() - self.start_time)
        msg = "Ти виграв! 🎉\n" if win else "Гру завершено. 💣\n"
        msg += f"Час: {elapsed} сек\nХоди: {self.moves}"
        if win:
            SoundManager.play_win_sound()
        else:
            SoundManager.play_lose_sound()

        self.update_statistics(elapsed, self.moves, win)

        popup = tk.Toplevel(self)
        popup.title("Результат гри")
        popup.geometry("300x220")
        popup.resizable(False, False)

        tk.Label(popup, text=msg, font=("Arial", 14)).pack(pady=10)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        def restart():
            popup.destroy()
            self.controller.start_game(self.rows, self.cols, self.mines)

        tk.Button(btn_frame, text="Почати заново", command=restart).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Змінити складність",
                  command=lambda: [popup.destroy(), self.controller.show_frame("DifficultySelector")]).pack(
            side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Меню", width=18, command=lambda: [popup.destroy(), self.controller.show_frame("MainMenu")]).pack(side=tk.LEFT, padx=5)

    def update_statistics(self, elapsed_time, moves, win):
        filename = "stats.txt"
        level = f"{self.rows}x{self.cols}_{self.mines}min"
        stats = {}
        try:
            with open(filename, "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) == 2:
                        data = list(map(int, parts[1].split(",")))
                        stats[parts[0]] = {
                            "games": data[0], "wins": data[1],
                            "total_time": data[2], "total_moves": data[3],
                            "best_time": data[4], "best_moves": data[5]
                        }
        except FileNotFoundError:
            pass

        if level not in stats:
            stats[level] = {
                "games": 0, "wins": 0, "total_time": 0,
                "total_moves": 0, "best_time": 0, "best_moves": 0
            }

        stats[level]["games"] += 1
        if win:
            stats[level]["wins"] += 1
            stats[level]["total_time"] += elapsed_time
            stats[level]["total_moves"] += moves
            if stats[level]["best_time"] == 0 or elapsed_time < stats[level]["best_time"]:
                stats[level]["best_time"] = elapsed_time
            if stats[level]["best_moves"] == 0 or moves < stats[level]["best_moves"]:
                stats[level]["best_moves"] = moves

        with open(filename, "w") as f:
            for lvl, data in stats.items():
                f.write(f"{lvl}:{data['games']},{data['wins']},{data['total_time']},{data['total_moves']},{data['best_time']},{data['best_moves']}\n")

if __name__ == "__main__":
    app = App()
    app.mainloop()
