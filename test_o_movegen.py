import unittest
from copy import deepcopy
from types import SimpleNamespace

from board import Board
from game import Game
from o_movegen import fits, movegen_o_piece
from piece import Piece


def empty_matrix():
    return [[None for _ in range(10)] for _ in range(40)]


def roof_and_shelf():
    matrix = empty_matrix()
    for row in (29, 32):
        for column in (4, 5):
            matrix[row][column] = "g"
    return matrix


class FitsTests(unittest.TestCase):
    def test_square_fits_at_all_four_board_corners(self):
        matrix = empty_matrix()
        for x, y in ((0, 0), (8, 0), (0, 38), (8, 38)):
            with self.subTest(x=x, y=y):
                self.assertTrue(fits(matrix, x, y))

    def test_square_cannot_cross_any_boundary(self):
        matrix = empty_matrix()
        for x, y in ((-1, 17), (9, 17), (4, -1), (4, 39)):
            with self.subTest(x=x, y=y):
                self.assertFalse(fits(matrix, x, y))

    def test_each_of_the_four_cells_must_be_none(self):
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            for occupied in ("g", 0, "", False):
                with self.subTest(dx=dx, dy=dy, occupied=occupied):
                    matrix = empty_matrix()
                    matrix[17 + dy][4 + dx] = occupied
                    self.assertFalse(fits(matrix, 4, 17))


class MovegenOPieceTests(unittest.TestCase):
    def setUp(self):
        self.board = Board(800, 800, 0, 280, 3, 4, "black", "white")
        self.piece = Piece("o", current=True)

    def checked_paths(self):
        paths = {}
        for move in movegen_o_piece(self.piece, self.board):
            path = move["path"]
            self.assertIsInstance(path, list)
            piece = deepcopy(self.piece)
            game = SimpleNamespace(current=piece, board=self.board)
            for action in path:
                if action == "sd":
                    old_y = piece.y
                    Game.drop(game)
                    self.assertGreater(piece.y, old_y)
                else:
                    self.assertIn(action, ("left", "right"))
                    piece.x += 1 if action == "right" else -1
                    self.assertTrue(piece.collide(self.board.matrix, action))

            self.assertEqual(move["state"], (piece.x, piece.y, self.piece.rotation % 4))
            position = (piece.x, piece.y)
            Game.drop(game)
            self.assertEqual(piece.y, position[1])
            self.assertNotIn(position, paths)
            paths[position] = path
        self.assertEqual(list(paths), sorted(paths))
        return paths

    def test_empty_board_has_nine_shortest_paths_to_the_floor(self):
        paths = self.checked_paths()
        self.assertEqual(list(paths), [(x, 38) for x in range(9)])
        for (x, y), path in paths.items():
            self.assertEqual(len(path), abs(x - self.piece.x) + 1)

    def test_already_grounded_piece_has_an_empty_path(self):
        self.piece.x, self.piece.y = 1, 38
        self.assertEqual(self.checked_paths()[(1, 38)], [])

    def test_blocked_spawn_has_no_moves(self):
        self.board.matrix[17][4] = "g"
        self.assertEqual(movegen_o_piece(self.piece, self.board), [])

    def test_out_of_bounds_start_has_no_moves(self):
        for start in ((-1, 17), (9, 17), (4, -1), (4, 39)):
            with self.subTest(start=start):
                self.piece.x, self.piece.y = start
                self.assertEqual(movegen_o_piece(self.piece, self.board), [])

    def test_one_cell_well_cannot_hold_an_o_piece(self):
        for y in range(20, 40):
            self.board.matrix[y] = [None if x == 4 else "g" for x in range(10)]
        self.assertFalse(fits(self.board.matrix, 4, 20))
        self.assertEqual(list(self.checked_paths()), [(x, 18) for x in range(9)])

    def test_can_slide_under_an_overhang_after_landing(self):
        self.board.matrix[37][4] = self.board.matrix[37][5] = "g"
        paths = self.checked_paths()
        self.assertEqual(paths[(4, 35)], ["sd"])
        self.assertEqual(len(paths[(4, 38)]), 5)
        self.assertEqual(paths[(4, 38)][2], "sd")

    def test_sealed_cavity_is_not_a_reachable_placement(self):
        for x in range(3, 7):
            self.board.matrix[37][x] = "g"
        for y in (38, 39):
            self.board.matrix[y][3] = self.board.matrix[y][6] = "g"
        self.assertTrue(fits(self.board.matrix, 4, 38))
        self.assertNotIn((4, 38), self.checked_paths())

    def test_full_drop_cannot_stop_at_a_midair_side_entrance(self):
        self.board.matrix = roof_and_shelf()
        self.assertTrue(fits(self.board.matrix, 4, 30))
        self.assertFalse(fits(self.board.matrix, 4, 31))
        moves = self.checked_paths()
        self.assertIn((4, 27), moves)
        self.assertNotIn((4, 30), moves)

    def test_current_piece_position_can_enter_the_same_open_sided_pocket(self):
        self.board.matrix = roof_and_shelf()
        self.piece.x, self.piece.y = 2, 30
        moves = self.checked_paths()
        self.assertIn((4, 30), moves)
        self.assertNotIn((4, 27), moves)

    def test_current_piece_x_is_used_instead_of_spawn_x(self):
        self.board.matrix = roof_and_shelf()
        self.piece.x, self.piece.y = 4, 29
        self.assertEqual(movegen_o_piece(self.piece, self.board), [])
        self.piece.x = 2
        self.assertTrue(self.checked_paths())

    def test_generation_preserves_board_and_current_piece(self):
        self.board.matrix = roof_and_shelf()
        self.piece.rotation = -1
        original_board = deepcopy(vars(self.board))
        original_piece = deepcopy(vars(self.piece))
        self.checked_paths()
        self.assertEqual(vars(self.board), original_board)
        self.assertEqual(vars(self.piece), original_piece)

    def test_o_rotations_have_equivalent_placements(self):
        self.board.matrix = roof_and_shelf()
        expected = list(self.checked_paths())
        for rotation in (-1, 0, 1, 2, 3, 4):
            with self.subTest(rotation=rotation):
                self.piece.rotation = rotation
                self.assertEqual(list(self.checked_paths()), expected)

    def test_other_piece_types_raise_value_error(self):
        for piece_type in ("i", "t", "j", "l", "s", "z"):
            with self.subTest(piece_type=piece_type):
                with self.assertRaises(ValueError):
                    movegen_o_piece(Piece(piece_type), self.board)

    def test_malformed_board_dimensions_raise_value_error(self):
        too_short = empty_matrix()[:-1]
        too_tall = empty_matrix() + [[None] * 10]
        narrow_row = empty_matrix()
        narrow_row[20] = [None] * 9
        wide_row = empty_matrix()
        wide_row[20] = [None] * 11
        for matrix in ([], too_short, too_tall, narrow_row, wide_row):
            with self.subTest(height=len(matrix)):
                self.board.matrix = matrix
                with self.assertRaises(ValueError):
                    movegen_o_piece(self.piece, self.board)


if __name__ == "__main__":
    unittest.main()
