import pygame
from math import sqrt

class Piece:
    PIECES = ['p', 'g', 'z', 'l', 'o', 's', 'i', 'j', 't']
    MINO_SIZE = 28
    MINO_MAPS = {
        # represents filled in minos of a 3x3 grid, except 4x4 for I and 2x2 for O
        # 0 is base state, 1 is ccw rotation, 2 is 180 rotation, 3 is cw rotation
        'z': [[1, 1, 0, 0, 1, 1, 0, 0, 0], [0, 1, 0, 1, 1, 0, 1, 0, 0], [0, 0, 0, 1, 1, 0, 0, 1, 1], [0, 0, 1, 0, 1, 1, 0, 1, 0]],
        'l': [[0, 0, 1, 1, 1, 1, 0, 0, 0], [1, 1, 0, 0, 1, 0, 0, 1, 0], [0, 0, 0, 1, 1, 1, 1, 0, 0], [0, 1, 0, 0, 1, 0, 0, 1, 1]],
        's': [[0, 1, 1, 1, 1, 0, 0, 0, 0], [1, 0, 0, 1, 1, 0, 0, 1, 0], [0, 0, 0, 0, 1, 1, 1, 1, 0], [0, 1, 0, 0, 1, 1, 0, 0, 1]],
        'j': [[1, 0, 0, 1, 1, 1, 0, 0, 0], [0, 1, 0, 0, 1, 0, 1, 1, 0], [0, 0, 0, 1, 1, 1, 0, 0, 1], [0, 1, 1, 0, 1, 0, 0, 1, 0]],
        't': [[0, 1, 0, 1, 1, 1, 0, 0, 0], [0, 1, 0, 1, 1, 0, 0, 1, 0], [0, 0, 0, 1, 1, 1, 0, 1, 0], [0, 1, 0, 0, 1, 1, 0, 1, 0]],
        'i': [[0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]],
        'o': [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]
    }

    # index is based on rotation number after rotation is performed
    CCW_KICKS = {
        # 0 is cw to base, 1 is base to ccw, 2 is ccw to 180, 3 is 180 to cw
        'i': [[(2, 0), (-1, 0), (2, 1), (-1, -2)], [(-1, 0), (2, 0), (-1, 2), (2, -1)],
              [(-2, 0), (1, 0), (-2, -1), (1, 2)], [(1, 0), (-2, 0), (1, -2), (-2, 1)]],
        'other': [[(1, 0), (1, -1), (0, 2), (1, 2)], [(1, 0), (1, 1), (0, -2), (1, -2)],
              [(-1, 0), (-1, -1), (0, 2), (-1, 2)], [(-1, 0), (-1, 1), (0, -2), (-1, -2)]]
    }
    CW_KICKS = {
        # 0 is ccw to base, 1 is 180 to ccw, 2 is cw to 180, 3 is base to cw
        'i': [[(1, 0), (-2, -0), (1, -2), (-2, 1)], [(2, 0), (-1, 0), (2, 1), (-1, -2)],
              [(-1, 0), (2, 0), (-1, 2), (2, -1)], [(-2, 0), (1, 0), (-2, -1), (1, 2)]],
        'other': [[(-1, 0), (-1, -1), (0, 2), (-1, 2)], [(1, 0), (1, 1), (0, -2), (1, -2)],
                  [(1, 0), (1, -1), (0, 2), (1, 2)], [(-1, 0), (-1, 1), (0, -2), (-1, -2)]]

    }
    # 0 is 180 to base, 1 is cw to ccw, 2 is base to 180, 3 is ccw to cw
    KICKS_180 = [[(0, -1), (-1, -1), (1, -1), (-1, 0), (1, 0)], [(1, 0), (1, 2), (1, 1), (0, 2), (0, 1)],
         [(0, 1), (1, 1), (-1, 1), (1, 0), (-1, 0)], [(-1, 0), (-1, 2), (-1, 1), (0, 2), (0, 1)],]
    def __init__(self, piece_type, rotation=0, current=False):
        self.type = piece_type
        self.rotation = rotation
        self.x = 4 if self.type == 'o' else 3
        self.y = 17
        self.current = current

    def draw(self, screen, skin, x, y, ghost=False, ghost_y=None):
        crop_x = Piece.PIECES.index(self.type) * Piece.MINO_SIZE
        mino = pygame.Rect(crop_x, 0, Piece.MINO_SIZE, Piece.MINO_SIZE)
        self.rotation %= 4
        mino_map = Piece.MINO_MAPS[self.type][self.rotation]
        dimension = 4 if self.type == 'i' else 2 if self.type == 'o' else 3
        for i in range(dimension):
            y_pos = i * Piece.MINO_SIZE
            for j in range(dimension):
                x_pos = j * Piece.MINO_SIZE
                if mino_map[i * dimension + j] == 1:
                    if self.current:
                        if ghost:
                            screen.blit(skin, (x + self.x * Piece.MINO_SIZE + x_pos,
                                               y + (ghost_y - 20) * Piece.MINO_SIZE + y_pos), area=mino)
                        else:
                            screen.blit(skin, (x + self.x * Piece.MINO_SIZE + x_pos, y + (self.y - 20) * Piece.MINO_SIZE + y_pos), area=mino)
                    else:
                        screen.blit(skin, (x + x_pos, y + y_pos), area=mino)

    def collide(self, matrix, action, ghost_y=None):
        self.rotation %= 4
        my_map = Piece.MINO_MAPS[self.type][self.rotation]
        collision = False
        dimension = int(sqrt(len(my_map)))
        for index, mino in enumerate(my_map):
            if mino:
                x = index % dimension + self.x
                y = index // dimension + self.y if not ghost_y else index // dimension + ghost_y
                if x < 0 or x > 9 or y > 39 or matrix[y][x]:
                    collision = True
                    break

        if action == 'ghost':
            return -1 if collision else 0
        if collision:
            if action in ('left', 'right', 'sd'):
                x_change = 1 if action == 'left' else -1 if action == 'right' else 0
                y_change = -1 if action == 'sd' else 0
                self.x += x_change
                self.y += y_change
            else:
                force_spin = False
                kick_table = 'i' if self.type == 'i' else 'other'
                kicks = Piece.CW_KICKS[kick_table][self.rotation] if action == 'cw' \
                    else Piece.CCW_KICKS[kick_table][self.rotation] if action == 'ccw' else Piece.KICKS_180[self.rotation]
                for index, kick in enumerate(kicks):
                    valid_kick = True
                    self.x += kick[0]
                    self.y -= kick[1]
                    for index, mino in enumerate(my_map):
                        if mino:
                            x = index % dimension + self.x
                            y = index // dimension + self.y
                            if x < 0 or x > 9 or y > 39 or matrix[y][x]:
                                valid_kick = False
                                break
                    if valid_kick:
                        force_spin = index == 4 and self.type == 't'
                        break
                    self.x -= kick[0]
                    self.y += kick[1]
                if not valid_kick:
                    revert = 1 if action == 'cw' else -1 if action == 'ccw' else 2
                    self.rotation += revert
                if action == 'cw' or action == 'ccw':
                    return force_spin

    def lock_piece(self, matrix):
        spin = 'none'
        t_corners = 0
        t_corners_faced = 0
        my_map = Piece.MINO_MAPS[self.type]
        dimension = int(sqrt(len(my_map[self.rotation])))
        for index, mino in enumerate(my_map[self.rotation]):
            corner_filled = False
            x = index % dimension + self.x
            y = index // dimension + self.y
            if self.type == 't' and index in (0, 2, 6, 8):
                corner_filled = y > 39 or x < 0 or x > 9 or matrix[y][x]
                if corner_filled:
                    t_corners += 1
                    t_corners_faced += 1 if self.rotation == 0 and index in (0, 2) or self.rotation == 1 and index in (0, 6) or self.rotation == 2 and index in (6, 8) or self.rotation == 3 and index in (2, 8) else 0
            if mino:
                matrix[y][x] = self.type
                if self.type != 't':
                    if matrix[y - 1][x] and not my_map[self.rotation][index - dimension]:
                        print(matrix[y - 1][x])
                        spin = 'mini'
            spin = 'none' if self.type == 't' and t_corners < 3 else f'{self.type.upper()}-spin' if t_corners_faced == 2 else f'Mini {self.type.upper()}-spin' if spin != 'none' else 'none'
        return matrix, spin

    def test_lockout(self, game, matrix):
        my_map = Piece.MINO_MAPS[self.type]
        dimension = int(sqrt(len(my_map[self.rotation])))
        for index, mino in enumerate(my_map[self.rotation]):
            if mino:
                x = index % dimension + self.x
                y = index // dimension + self.y
                if matrix[y][x] or game.lines_cleared >= 40:
                    game.board.matrix = [['p' if item is not None else None for item in row] for row in matrix]
                    return True
        return False

    def reset_pos(self):
        self.rotation = 0
        self.x = 4 if self.type == 'o' else 3
        self.y = 17