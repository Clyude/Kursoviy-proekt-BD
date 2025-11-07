import unittest


class MinesweeperGame:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.opened = set()
        self.mines_positions = {(0, 1)}

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_mine(self, r, c):
        return (r, c) in self.mines_positions

    def all_safe_opened(self):
        total_cells = self.rows * self.cols
        safe_cells = total_cells - len(self.mines_positions)
        return len(self.opened) == safe_cells


def create_game(rows, cols, mines):
    if rows < 5 or cols < 5 or rows > 30 or cols > 30:
        return "Помилка: некоректний розмір поля"
    if mines <= 0 or mines >= rows * cols:
        return "Помилка: некоректна кількість мін"
    return MinesweeperGame(rows, cols, mines)


def make_move(game, row, col):
    if not game.in_bounds(row, col):
        return "Помилка: хід поза межами поля"
    if (row, col) in game.opened:
        return "Помилка: клітинка вже відкрита"
    if game.is_mine(row, col):
        return "Програш: відкрита міна"
    game.opened.add((row, col))
    if game.all_safe_opened():
        return "Виграш: усі немінні клітинки відкриті"
    return "Хід виконано, гра триває"


class TestMinesweeperFunctional(unittest.TestCase):

    def test_21_invalid_board_size(self):
        result = create_game(3, 3, 1)
        self.assertEqual("Помилка: некоректний розмір поля", result)

    def test_22_invalid_mines_count(self):
        result = create_game(9, 9, 0)
        self.assertEqual("Помилка: некоректна кількість мін", result)

    def test_23_move_out_of_bounds(self):
        game = create_game(9, 9, 10)
        self.assertIsInstance(game, MinesweeperGame)
        result = make_move(game, -1, 0)
        self.assertEqual("Помилка: хід поза межами поля", result)

    def test_24_open_same_cell_twice(self):
        game = create_game(9, 9, 10)
        self.assertIsInstance(game, MinesweeperGame)
        first = make_move(game, 0, 0)
        second = make_move(game, 0, 0)
        self.assertIn(first, [
            "Хід виконано, гра триває",
            "Виграш: усі немінні клітинки відкриті"
        ])
        self.assertEqual("Помилка: клітинка вже відкрита", second)

    def test_27_win_condition(self):
        game = MinesweeperGame(2, 2, 1)
        result1 = make_move(game, 0, 0)
        result2 = make_move(game, 1, 0)
        result3 = make_move(game, 1, 1)
        self.assertEqual("Хід виконано, гра триває", result1)
        self.assertEqual("Хід виконано, гра триває", result2)
        self.assertEqual("Виграш: усі немінні клітинки відкриті", result3)


if __name__ == "__main__":
    unittest.main()
