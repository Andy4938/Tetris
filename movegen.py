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
        for state in self.final_states:
            if state.spin in ('mini', 't-spin'):
                print(f'{state}, {'mini' or 't-spin' in state}')
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
    def __init__(self, type, x=3, y=17, rotation=0, spin='None'):
        self.type = type
        self.rotation = rotation
        self.x = x
        self.y = y
        self.spin = spin

    def __eq__(self, other):
        # return (self.x, self.y, self.rotation) == (other.x, other.y, other.rotation)
        return (self.type, self.x, self.y, self.rotation, self.spin) == (other.type, other.x, other.y, other.rotation,
                                                                          other.spin)

    def __hash__(self):
        # return hash((self.type, self.x, self.y, self.rotation))
        return hash((self.type, self.x, self.y, self.rotation, self.spin))

    def __repr__(self):
        return f'({self.type}, {self.x}, {self.y}, {self.rotation}, {self.spin})'

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
            for k, (dx, dy) in enumerate([(0, 0)] + list(kicks)):
                spin = 'None'
                valid_rotation = True
                t_corners = 0
                t_corners_faced = 0
                vertical_check = False
                left_check = False
                right_check = False
                for index, mino in enumerate(my_map):
                    x = index % dimension + self.x + dx
                    y = index // dimension + self.y - dy
                    if self.type == 't' and index in (0, 2, 6, 8):
                        corner_filled = y > 39 or x < 0 or x > 9 or matrix[y][x]
                        if corner_filled:
                            t_corners += 1
                            t_corners_faced += 1 if (new_r == 0 and index in (0,2) or new_r == 1 and
                                                     index in (0, 6) or new_r == 2 and index in (6,8) or
                                                     new_r == 3 and index in (2, 8)) else 0
                    if mino:
                        if x < 0 or x > 9 or y > 39 or matrix[y][x]:
                            valid_rotation = False
                            break
                        if matrix[y - 1][x] and (index - dimension < 0 or not my_map[index - dimension]):
                            vertical_check = True
                        left_mino = False if index % dimension == 0 else True
                        if x <= 0 or (matrix[y][x - 1] and (not left_mino or not my_map[index - 1])):
                            left_check = True
                        right_mino = None if (index + 1) % dimension == 0 else True
                        if x >= 9 or (matrix[y][x + 1] and (not right_mino or not my_map[index + 1])):
                            right_check = True
                        if vertical_check and left_check and right_check:
                            spin = 'mini'
                if valid_rotation:
                    if self.type == 't':
                        spin = spin if t_corners < 3 else 't-spin' if t_corners_faced == 2 else 'mini'
                        if spin == 'mini' and k == 4 and input != '180':
                            spin = 't-spin'
                    else:
                        spin = f'mini' if spin != 'None' else 'None'
                    return PieceState(self.type, self.x + dx, self.y - dy, new_r, spin)
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
            return PieceState(self.type, self.x + dx, self.y, self.rotation, 'None')

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
        return PieceState(self.type, self.x, self.y + dy, self.rotation, self.spin if dy == 0 else 'None')

