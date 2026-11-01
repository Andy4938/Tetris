import unittest
from copy import deepcopy
from types import SimpleNamespace

from board import Board
from game import Game
from j_movegen import cells, fits, movegen_j_piece, rotate
from piece import Piece


def empty_matrix():
    return [[None for _ in range(10)] for _ in range(40)]


def spin_slot():
    matrix = empty_matrix()
    for y in range(36, 40):
        for x in range(10):
            matrix[y][x] = "g"
    for x, y in ((3, 36), (4, 36), (3, 37), (3, 38), (4, 38), (5, 38)):
        matrix[y][x] = None
    return matrix


class FitsTests(unittest.TestCase):
    def test_cells_match_piece_mino_maps(self):
        for rotation in range(4):
            with self.subTest(rotation=rotation):
                expected = {
                    (index % 3, index // 3)
                    for index, filled in enumerate(Piece.MINO_MAPS["j"][rotation])
                    if filled
                }
                self.assertEqual(set(cells(0, 0, rotation)), expected)

    def test_cannot_cross_any_boundary(self):
        matrix = empty_matrix()
        for x, y, rotation in ((-1, 17, 0), (8, 17, 0), (3, -1, 0), (3, 39, 0), (-2, 17, 1), (9, 17, 3)):
            with self.subTest(x=x, y=y, rotation=rotation):
                self.assertFalse(fits(matrix, x, y, rotation))

    def test_every_cell_must_be_none(self):
        for rotation in range(4):
            for cx, cy in cells(3, 17, rotation):
                for occupied in ("g", 0, "", False):
                    with self.subTest(rotation=rotation, cell=(cx, cy), occupied=occupied):
                        matrix = empty_matrix()
                        matrix[cy][cx] = occupied
                        self.assertFalse(fits(matrix, 3, 17, rotation))

    def test_rotation_matches_game_kicks(self):
        matrix = spin_slot()
        for x in range(-1, 9):
            for y in range(30, 38):
                for rotation in range(4):
                    if not fits(matrix, x, y, rotation):
                        continue
                    for action, step in (("cw", -1), ("ccw", 1), ("180", 2)):
                        with self.subTest(x=x, y=y, rotation=rotation, action=action):
                            piece = Piece("j", rotation=rotation)
                            piece.x, piece.y = x, y
                            piece.rotation += step
                            result = piece.collide(matrix, action)
                            failed = result if action == "180" else result[1]
                            expected = rotate(matrix, x, y, rotation, action)
                            if failed:
                                self.assertIsNone(expected)
                            else:
                                self.assertEqual(expected, (piece.x, piece.y, piece.rotation % 4))


class MovegenJPieceTests(unittest.TestCase):
    def setUp(self):
        self.board = Board(800, 800, 0, 280, 3, 4, "black", "white")
        self.piece = Piece("j", current=True)

    def replay(self, path):
        piece = deepcopy(self.piece)
        game = SimpleNamespace(current=piece, board=self.board)
        for action in path:
            if action == "sd":
                old_y = piece.y
                Game.drop(game)
                self.assertGreater(piece.y, old_y)
            elif action in ("left", "right"):
                piece.x += 1 if action == "right" else -1
                self.assertTrue(piece.collide(self.board.matrix, action))
            else:
                piece.rotation += {"cw": -1, "ccw": 1, "180": 2}[action]
                result = piece.collide(self.board.matrix, action)
                failed = result if action == "180" else result[1]
                self.assertFalse(failed)
        return piece

    def checked_moves(self):
        moves = {}
        for move in movegen_j_piece(self.piece, self.board):
            path = move["path"]
            self.assertIsInstance(path, list)
            piece = self.replay(path)
            state = (piece.x, piece.y, piece.rotation % 4)
            self.assertEqual(move["state"], state)
            self.assertFalse(fits(self.board.matrix, piece.x, piece.y + 1, piece.rotation % 4))
            self.assertNotIn(state, moves)
            moves[state] = path
        self.assertEqual(list(moves), sorted(moves))
        return moves

    def test_empty_board_has_thirty_four_landings(self):
        moves = self.checked_moves()
        self.assertEqual(len(moves), 34)
        for state in moves:
            self.assertEqual(max(cy for _, cy in cells(*state)), 39)
        counts = [sum(1 for state in moves if state[2] == rotation) for rotation in range(4)]
        self.assertEqual(counts, [8, 9, 8, 9])

    def test_every_landing_has_a_distinct_footprint(self):
        footprints = [frozenset(cells(*state)) for state in self.checked_moves()]
        self.assertEqual(len(footprints), len(set(footprints)))

    def test_already_grounded_piece_has_an_empty_path(self):
        self.piece.x, self.piece.y = 0, 38
        self.assertEqual(self.checked_moves()[(0, 38, 0)], [])

    def test_blocked_spawn_has_no_moves(self):
        self.board.matrix[18][4] = "g"
        self.assertEqual(movegen_j_piece(self.piece, self.board), [])

    def test_out_of_bounds_start_has_no_moves(self):
        for start in ((-1, 17), (8, 17), (3, -1), (3, 39)):
            with self.subTest(start=start):
                self.piece.x, self.piece.y = start
                self.assertEqual(movegen_j_piece(self.piece, self.board), [])

    def test_can_tuck_under_an_overhang(self):
        for x in range(0, 4):
            self.board.matrix[37][x] = "g"
        moves = self.checked_moves()
        self.assertIn((0, 38, 0), moves)
        self.assertIn("sd", moves[(0, 38, 0)])
        self.assertEqual(moves[(0, 38, 0)][-1], "left")

    def test_kick_into_covered_slot(self):
        self.board.matrix = spin_slot()
        moves = self.checked_moves()
        self.assertIn((3, 37, 0), moves)
        self.assertEqual(moves[(3, 37, 0)][-1], "ccw")

    def test_sealed_cavity_is_not_reachable(self):
        for x in range(2, 7):
            self.board.matrix[36][x] = "g"
        for y in (37, 38, 39):
            self.board.matrix[y][2] = self.board.matrix[y][6] = "g"
        self.assertTrue(fits(self.board.matrix, 3, 37, 0))
        moves = self.checked_moves()
        self.assertFalse(any(cy > 36 and 3 <= cx <= 5 for state in moves for cx, cy in cells(*state)))

    def test_current_rotation_is_used_as_start(self):
        self.piece.rotation = -1
        self.piece.x, self.piece.y = 0, 37
        moves = self.checked_moves()
        self.assertEqual(len(moves), 34)
        self.assertEqual(moves[(0, 37, 3)], [])

    def test_generation_preserves_board_and_current_piece(self):
        self.board.matrix = spin_slot()
        self.piece.rotation = -1
        original_board = deepcopy(vars(self.board))
        original_piece = deepcopy(vars(self.piece))
        movegen_j_piece(self.piece, self.board)
        self.assertEqual(vars(self.board), original_board)
        self.assertEqual(vars(self.piece), original_piece)

    def test_other_piece_types_raise_value_error(self):
        for piece_type in ("i", "o", "t", "l", "s", "z"):
            with self.subTest(piece_type=piece_type):
                with self.assertRaises(ValueError):
                    movegen_j_piece(Piece(piece_type), self.board)

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
                    movegen_j_piece(self.piece, self.board)


if __name__ == "__main__":
    unittest.main()
