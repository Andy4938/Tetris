from piece import Piece
from board import Board
from collections import deque


BOARD_WIDTH = 10
BOARD_HEIGHT = 40


def fits(matrix, x, y):
    if x < 0 or x + 1 >= BOARD_WIDTH or y < 0 or y + 1 >= BOARD_HEIGHT:
        return False

    return (
        matrix[y][x] is None
        and matrix[y][x + 1] is None
        and matrix[y + 1][x] is None
        and matrix[y + 1][x + 1] is None
    )


def movegen_o_piece(piece: Piece, board: Board):
    if piece.type != 'o':
        raise ValueError("piece must be an O-piece")

    matrix = board.matrix
    if len(matrix) != BOARD_HEIGHT or any(
        len(row) != BOARD_WIDTH for row in matrix
    ):
        raise ValueError("matrix must have 40 rows and 10 columns")

    start_x, start_y = piece.x, piece.y
    if not fits(matrix, start_x, start_y):
        return []

    start = (start_x, start_y)
    rotation = piece.rotation % 4
    queue = deque([(start, [])])
    visited = {start}
    landings = []

    while queue:
        (x, y), path = queue.popleft()

        drop_y = y
        while fits(matrix, x, drop_y + 1):
            drop_y += 1
        if drop_y == y:
            landings.append({"state": (x, y, rotation), "path": path})

        candidates = (
            ("left", (x - 1, y)),
            ("right", (x + 1, y)),
            ("sd", (x, drop_y)),
        )
        for action, position in candidates:
            if position not in visited and fits(matrix, *position):
                visited.add(position)
                queue.append((position, path + [action]))

    return sorted(landings, key=lambda move: move["state"])
