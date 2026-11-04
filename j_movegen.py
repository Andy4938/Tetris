from piece import Piece
from board import Board
from collections import deque


BOARD_WIDTH = 10
BOARD_HEIGHT = 40

J_CELLS = tuple(
    tuple((index % 3, index // 3) for index, filled in enumerate(shape) if filled)
    for shape in Piece.MINO_MAPS['j']
)

ROTATIONS = {
    'cw': (-1, Piece.CW_KICKS['other']),
    'ccw': (1, Piece.CCW_KICKS['other']),
    '180': (2, Piece.KICKS_180),
}


def cells(x, y, rotation):
    return [(x + dx, y + dy) for dx, dy in J_CELLS[rotation]]


def fits(matrix, x, y, rotation):
    for cx, cy in cells(x, y, rotation):
        if cx < 0 or cx >= BOARD_WIDTH or cy < 0 or cy >= BOARD_HEIGHT:
            return False
        if matrix[cy][cx] is not None:
            return False

    return True


def rotate(matrix, x, y, rotation, action):
    step, table = ROTATIONS[action]
    new_rotation = (rotation + step) % 4
    for kick_x, kick_y in ((0, 0),) + tuple(table[new_rotation]):
        candidate = (x + kick_x, y - kick_y, new_rotation)
        if fits(matrix, *candidate):
            return candidate

    return None


def drop(matrix, x, y, rotation):
    while fits(matrix, x, y + 1, rotation):
        y += 1
    return y


def movegen_j_piece(piece: Piece, board: Board):
    if piece.type != 'j':
        raise ValueError("piece must be a J-piece")

    matrix = board.matrix
    if len(matrix) != BOARD_HEIGHT or any(
        len(row) != BOARD_WIDTH for row in matrix
    ):
        raise ValueError("matrix must have 40 rows and 10 columns")

    start = (piece.x, piece.y, piece.rotation % 4)
    if not fits(matrix, *start):
        return []

    queue = deque([(start, [])])
    visited = {start}
    landings = []

    while queue:
        (x, y, rotation), path = queue.popleft()

        drop_y = drop(matrix, x, y, rotation)
        if drop_y == y:
            landings.append({"state": (x, y, rotation), "path": path})

        candidates = (
            ("left", (x - 1, y, rotation)),
            ("right", (x + 1, y, rotation)),
            ("cw", rotate(matrix, x, y, rotation, 'cw')),
            ("ccw", rotate(matrix, x, y, rotation, 'ccw')),
            ("180", rotate(matrix, x, y, rotation, '180')),
            ("sd", (x, drop_y, rotation)),
        )
        for action, position in candidates:
            if (
                position is not None
                and position not in visited
                and fits(matrix, *position)
            ):
                visited.add(position)
                queue.append((position, path + [action]))

    return sorted(landings, key=lambda move: move["state"])
