from piece import Piece
from math import sqrt
from collections import deque

class Movegen:
    INPUTS = ['right', 'left', 'cw', 'ccw', '180', 'sd']
    def __init__(self, matrix):
        self.matrix = matrix
        self.states = []
        self.final_states = []
        self.previous = {}

    def generate(self, piece_type):
        state = PieceState(piece_type, x=4 if piece_type == 'o' else 3)
        self.search(state)
        print(self.final_states)
        print(len(self.final_states), len(set(self.final_states)))

    def search(self, spawn):
        self.states = []
        self.final_states = []
        self.previous = {spawn: None}
        queue = deque([spawn])
        while queue:
            state = queue.popleft()
            if self._check_final_state(state):
                  self.final_states.append(state)
            for move in Movegen.INPUTS:
                nxt = state.move(move, self.matrix)
                if nxt is not None and nxt not in self.previous:
                    self.previous[nxt] = (state, move)
                    queue.append(nxt)
                    self.states.append(state)

    def _check_final_state(self, state):
        my_map = Piece.MINO_MAPS[state.type][state.rotation]
        dimension = int(sqrt(len(my_map)))
        for index, mino in enumerate(my_map):
            if mino:
                x = index % dimension + state.x
                y = index // dimension + state.y
                if y == 39 or self.matrix[y + 1][x]:
                    return True
        return False

class PieceState:
    def __init__(self, type, x=3, y=17, rotation=0, Spun=False):
        self.type = type
        self.rotation = rotation
        self.x = x
        self.y = y
        self.spun = Spun

    def __eq__(self, other):
        return (self.x, self.y, self.rotation) == (other.x, other.y, other.rotation)
        # return (self.type, self.x, self.y, self.rotation, self.spun) == (other.type, other.x, other.y, other.rotation,
        #                                                                  other.spun)

    def __hash__(self):
        return hash((self.type, self.x, self.y, self.rotation, self.spun))

    def __repr__(self):
        return f'({self.type}, {self.x}, {self.y}, {self.rotation}, {self.spun})'

    def move(self, input, matrix):
        if input in ('cw', 'ccw', '180'):
            new_r = (self.rotation + {'cw': -1, 'ccw': 1, '180': 2}[input]) % 4
            if input == '180':
                kicks = Piece.KICKS_180[new_r]
            else:
                table = (Piece.CW_KICKS if input == 'cw' else Piece.CCW_KICKS)['i' if self.type == 'i' else 'other']
                kicks = table[new_r]
            my_map = Piece.MINO_MAPS[self.type][new_r]
            dimension = int(sqrt(len(my_map)))
            for dx, dy in [(0, 0)] + list(kicks):
                valid_rotation = True
                for map_index, mino in enumerate(my_map):
                    if mino:
                        x = map_index % dimension + self.x + dx
                        y = map_index // dimension + self.y - dy
                        if x < 0 or x > 9 or y > 39 or matrix[y][x]:
                            valid_rotation = False
                            break
                if valid_rotation:
                    return PieceState(self.type, self.x + dx, self.y - dy, new_r, True)
            return None

        my_map = Piece.MINO_MAPS[self.type][self.rotation]
        dimension = int(sqrt(len(my_map)))
        if input in ('right', 'left'):
            dx = 1 if input == 'right' else -1
            for map_index, mino in enumerate(my_map):
                if mino:
                    x = map_index % dimension + self.x + dx
                    y = map_index // dimension + self.y
                    if x < 0 or x > 9 or matrix[y][x]:
                        return None
            return PieceState(self.type, self.x + dx, self.y, self.rotation, False)

        # softdrop
        dropped = False
        dy = 0
        while not dropped:
            dy += 1
            for map_index, mino in enumerate(my_map):
                if mino:
                    x = map_index % dimension + self.x
                    y = map_index // dimension + self.y + dy
                    if y > 39 or matrix[y][x]:
                        dropped = True
        dy -= 1
        return PieceState(self.type, self.x, self.y + dy, self.rotation, self.spun if dy == 0 else False)

