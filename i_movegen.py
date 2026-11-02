from piece import Piece
from board import Board
from collections import deque


BOARD_WIDTH = 10
BOARD_HEIGHT = 40

# dx, dy of filled cells per rotation from MINO_MAPS
I_CELLS = tuple(
    tuple((index % 4, index // 4) for index, filled in enumerate(shape) if filled)
    for shape in Piece.MINO_MAPS['i']
)

# input is rotation change (cw is -1 in game)
ROTATIONS = (('cw', -1), ('ccw', 1), ('180', 2))


def cells(x, y, rot):
    return [(x + dx, y + dy) for dx, dy in I_CELLS[rot]]


def fits(matrix, x, y, rot):
    for cx, cy in cells(x, y, rot):
        if cx < 0 or cx >= BOARD_WIDTH or cy < 0 or cy >= BOARD_HEIGHT:
            return False
        if matrix[cy][cx] is not None:
            return False

    return True


def rotate(matrix, x, y, rot, action):
    # returns new (x, y, rot) or None
    change = dict(ROTATIONS)[action]
    new_rot = (rot + change) % 4
    if action == '180':
        kicks = Piece.KICKS_180[new_rot]
    else:
        table = Piece.CW_KICKS if action == 'cw' else Piece.CCW_KICKS
        kicks = table['i'][new_rot]

    # no kick first, kick dy positive = up
    for kick_x, kick_y in [(0, 0)] + list(kicks):
        candidate = (x + kick_x, y - kick_y, new_rot)
        if fits(matrix, *candidate):
            return candidate

    return None


def drop_y(matrix, x, y, rot):
    while fits(matrix, x, y + 1, rot):
        y += 1
    return y


def movegen_i_piece(piece: Piece, board: Board):
    # returns [{"state": (x, y, rot), "path": [inputs]}] sorted by state
    # sd = drop to floor, hard drop at the end not in path
    if piece.type != 'i':
        raise ValueError("piece must be an I-piece")

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
    landings = {}

    while queue:
        state, path = queue.popleft()
        x, y, rot = state

        floor_y = drop_y(matrix, x, y, rot)
        if floor_y == y:
            # key on cells, rot 0/2 and 1/3 overlap
            landings.setdefault(
                frozenset(cells(x, y, rot)), {"state": state, "path": path}
            )

        candidates = [
            ('left', (x - 1, y, rot)),
            ('right', (x + 1, y, rot)),
            ('sd', (x, floor_y, rot)),
        ]
        for action, _ in ROTATIONS:
            candidates.append((action, rotate(matrix, x, y, rot, action)))

        for action, position in candidates:
            if (
                position is not None
                and position not in visited
                and fits(matrix, *position)
            ):
                visited.add(position)
                queue.append((position, path + [action]))

    return sorted(landings.values(), key=lambda move: move["state"])
