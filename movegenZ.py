from collections import deque
from piece import Piece


class MoveGenZ:
    # state is (x, y, rotation), same coordinate system as Piece: x is 0-9 left to right,
    # y is 0-39 top to bottom, (x, y) is the top left of the 3x3 mino map
    TYPE = 'z'
    DIMENSION = 3
    SPAWN = (3, 17, 0)
    ROTATIONS = ('cw', 'ccw', '180')

    def __init__(self, matrix):
        self.matrix = matrix

    def get_minos(self, x, y, rotation):
        """Return the 4 board cells [(x, y), ...] the z piece fills in this state."""
        my_map = Piece.MINO_MAPS[self.TYPE][rotation % 4] # fetch properly rotated piece
        return [(index % self.DIMENSION + x, index // self.DIMENSION + y)
                for index, mino in enumerate(my_map) if mino]

    def is_valid(self, x, y, rotation):
        """Return True if the piece fits: every mino in bounds and on an empty cell."""
        for mino_x, mino_y in self.get_minos(x, y, rotation):
            # y < 0 isn't checked by Piece.collide, but matrix[-1] would wrap to the bottom row
            if mino_x < 0 or mino_x > 9 or mino_y < 0 or mino_y > 39 or self.matrix[mino_y][mino_x]:
                return False
        return True

    def drop_y(self, x, y, rotation):
        """Return the lowest y the piece reaches by falling straight down from (x, y)."""
        while self.is_valid(x, y + 1, rotation):
            y += 1
        return y

    def try_shift(self, state, dx):
        """Return the state moved dx columns (-1 left, 1 right), or None if blocked."""
        x, y, rotation = state
        return (x + dx, y, rotation) if self.is_valid(x + dx, y, rotation) else None

    def try_rotate(self, state, action):
        """Return the state after a 'cw', 'ccw' or '180' rotation, applying kicks, or None if every kick fails."""
        x, y, rotation = state
        change = -1 if action == 'cw' else 1 if action == 'ccw' else 2
        new_rotation = (rotation + change) % 4
        if self.is_valid(x, y, new_rotation):
            return x, y, new_rotation
        # kick tables are indexed by the rotation after rotating, same as Piece.collide
        kicks = Piece.CW_KICKS['other'][new_rotation] if action == 'cw' \
            else Piece.CCW_KICKS['other'][new_rotation] if action == 'ccw' else Piece.KICKS_180[new_rotation]
        for kick in kicks:
            if self.is_valid(x + kick[0], y - kick[1], new_rotation):
                return x + kick[0], y - kick[1], new_rotation
        return None

    def neighbors(self, state):
        """Return [(action, next_state), ...] for every input that changes the state."""
        moves = []
        for action, dx in (('left', -1), ('right', 1)):
            next_state = self.try_shift(state, dx)
            if next_state:
                moves.append((action, next_state))
        x, y, rotation = state
        bottom = self.drop_y(x, y, rotation)
        if bottom != y:
            moves.append(('sd', (x, bottom, rotation)))
        for action in self.ROTATIONS:
            next_state = self.try_rotate(state, action)
            if next_state:
                moves.append((action, next_state))
        return moves

    def is_resting(self, state):
        """Return True if the piece can't move down, i.e. a hard drop here locks in place."""
        x, y, rotation = state
        return not self.is_valid(x, y + 1, rotation)

    def normalize(self, state):
        """Return a key for the final placement so equivalent states dedupe."""
        # rotation 0 and 2 (or 1 and 3) landing on the same cells give the same key
        return frozenset(self.get_minos(*state))

    def generate_hard_drops(self):
        """Fast movegen: every placement reachable by rotating, shifting, then hard dropping from spawn.

        Returns {(cells, spin): (final_state, input_path)}. Skips tucks and spins.
        """
        results = {}
        if not self.is_valid(*self.SPAWN):
            return results
        starts = [(self.SPAWN, [])]
        for action in self.ROTATIONS:
            rotated = self.try_rotate(self.SPAWN, action)
            if rotated:
                starts.append((rotated, [action]))
        for start, rotate_path in starts:
            for action, dx in (('left', -1), ('right', 1)):
                state, path = start, list(rotate_path)
                while state:
                    x, y, rotation = state
                    final = (x, self.drop_y(x, y, rotation), rotation)
                    # the hard drop moving the piece cancels a spin, same as Game.drop setting last_input
                    last_action = path[-1] if path and final == state else 'hd'
                    key = (self.normalize(final), self.get_spin(final, last_action))
                    if key not in results:
                        results[key] = (final, path + ['hd'])
                    state = self.try_shift(state, dx)
                    path = path + [action]
        return results

    def generate_all_moves(self):
        """Full movegen: BFS over states from spawn, includes tucks and z-spins.

        Returns {(cells, spin): (final_state, input_path)}, each path is the shortest one found.
        """
        results = {}
        if not self.is_valid(*self.SPAWN):
            return results
        parents = {self.SPAWN: None}
        queue = deque([self.SPAWN])
        if self.is_resting(self.SPAWN):
            results[(self.normalize(self.SPAWN), '')] = (self.SPAWN, ['hd'])
        while queue:
            state = queue.popleft()
            for action, next_state in self.neighbors(state):
                # record placements per edge, so a spot reached by both a shift and a rotation
                # keeps its spin version even though the state itself is only visited once
                if self.is_resting(next_state):
                    key = (self.normalize(next_state), self.get_spin(next_state, action))
                    if key not in results:
                        results[key] = (next_state, self.build_path(parents, state) + [action, 'hd'])
                if next_state not in parents:
                    parents[next_state] = (state, action)
                    queue.append(next_state)
        return results

    def build_path(self, parents, state):
        """Walk the BFS parent map back from state to SPAWN and return the input list."""
        path = []
        while parents[state]:
            state, action = parents[state]
            path.append(action)
        path.reverse()
        return path

    def get_spin(self, state, last_action):
        """Return the spin type ('' or 'Mini Z-spin') a placement would score, mirroring Piece.lock_piece."""
        # only counts when last_action is a rotation, like Game.handle_event does
        if last_action not in self.ROTATIONS:
            return ''
        x, y, rotation = state
        my_map = Piece.MINO_MAPS[self.TYPE][rotation % 4]
        dimension = self.DIMENSION
        vertical_check = left_check = right_check = False
        for index, mino in enumerate(my_map):
            if not mino:
                continue
            mino_x = index % dimension + x
            mino_y = index // dimension + y
            # each side is blocked by the board, ignoring the piece's own minos
            if self.matrix[mino_y - 1][mino_x] and (index - dimension < 0 or not my_map[index - dimension]):
                vertical_check = True
            if mino_x <= 0 or (self.matrix[mino_y][mino_x - 1] and (index % dimension == 0 or not my_map[index - 1])):
                left_check = True
            if mino_x >= 9 or (self.matrix[mino_y][mino_x + 1] and ((index + 1) % dimension == 0 or not my_map[index + 1])):
                right_check = True
        # non-t pieces never face 2 corners in lock_piece, so a z can only score a mini
        return 'Mini Z-spin' if vertical_check and left_check and right_check else ''
