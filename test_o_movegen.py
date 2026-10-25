import unittest
from copy import deepcopy

from board import Board
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

    def test_empty_board_has_nine_floor_placements(self):
        self.assertEqual(
            movegen_o_piece(self.piece, self.board),
            [(x, 38) for x in range(9)],
        )

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
        self.assertEqual(
            movegen_o_piece(self.piece, self.board),
            [(x, 18) for x in range(9)],
        )

    def test_can_slide_under_an_overhang_after_landing(self):
        self.board.matrix[37][4] = self.board.matrix[37][5] = "g"
        moves = movegen_o_piece(self.piece, self.board)
        self.assertIn((4, 35), moves)
        self.assertIn((4, 38), moves)

    def test_sealed_cavity_is_not_a_reachable_placement(self):
        for x in range(3, 7):
            self.board.matrix[37][x] = "g"
        for y in (38, 39):
            self.board.matrix[y][3] = self.board.matrix[y][6] = "g"
        self.assertTrue(fits(self.board.matrix, 4, 38))
        self.assertNotIn((4, 38), movegen_o_piece(self.piece, self.board))

    def test_full_drop_cannot_stop_at_a_midair_side_entrance(self):
        self.board.matrix = roof_and_shelf()
        self.assertTrue(fits(self.board.matrix, 4, 30))
        self.assertFalse(fits(self.board.matrix, 4, 31))
        moves = movegen_o_piece(self.piece, self.board)
        self.assertIn((4, 27), moves)
        self.assertNotIn((4, 30), moves)

    def test_current_piece_position_can_enter_the_same_open_sided_pocket(self):
        self.board.matrix = roof_and_shelf()
        self.piece.x, self.piece.y = 2, 30
        moves = movegen_o_piece(self.piece, self.board)
        self.assertIn((4, 30), moves)
        self.assertNotIn((4, 27), moves)

    def test_current_piece_x_is_used_instead_of_spawn_x(self):
        self.board.matrix = roof_and_shelf()
        self.piece.x, self.piece.y = 4, 29
        self.assertEqual(movegen_o_piece(self.piece, self.board), [])
        self.piece.x = 2
        self.assertTrue(movegen_o_piece(self.piece, self.board))

    def test_generation_preserves_inputs_and_returns_unique_sorted_moves(self):
        self.board.matrix = roof_and_shelf()
        self.piece.rotation = 3
        original_board = deepcopy(vars(self.board))
        original_piece = deepcopy(vars(self.piece))
        moves = movegen_o_piece(self.piece, self.board)
        self.assertEqual(vars(self.board), original_board)
        self.assertEqual(vars(self.piece), original_piece)
        self.assertEqual(moves, sorted(set(moves)))

    def test_o_rotations_have_equivalent_placements(self):
        self.board.matrix = roof_and_shelf()
        expected = movegen_o_piece(self.piece, self.board)
        for rotation in range(4):
            with self.subTest(rotation=rotation):
                self.piece.rotation = rotation
                self.assertEqual(movegen_o_piece(self.piece, self.board), expected)

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
