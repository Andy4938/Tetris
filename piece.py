import pygame
from math import sqrt

class Piece:
    PIECES = ['p', 'g', 'z', 'l', 'o', 's', 'i', 'j', 't']
    MINO_SIZE = 30
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
    def __init__(self, piece_type, rotation=0, current=False):
        self.type = piece_type
        self.rotation = rotation
        self.x = 4 if self.type == 'o' else 3
        self.y = 17
        self.current = current

    def draw(self, screen, skin, x, y):
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
                        screen.blit(skin, (x + self.x * Piece.MINO_SIZE + x_pos, y + (self.y - 20) * Piece.MINO_SIZE + y_pos), area=mino)
                    else:
                        screen.blit(skin, (x + x_pos, y + y_pos), area=mino)

    def collide(self, matrix, action):
        my_map = Piece.MINO_MAPS[self.type][self.rotation]
        collision = False
        dimension = int(sqrt(len(my_map)))
        for index, mino in enumerate(my_map):
            if mino:
                x = index % dimension + self.x
                y = index // dimension + self.y
                if x < 0 or x > 9 or y > 39 or matrix[y][x]:
                    collision = True
                    break

        if collision:
            x_change = 1 if action == 'left' else -1 if action == 'right' else 0
            y_change = -1 if action == 'sd' else 0
            self.x += x_change
            self.y += y_change

    def lock_piece(self, matrix):
        my_map = Piece.MINO_MAPS[self.type]
        dimension = int(sqrt(len(my_map[self.rotation])))
        for index, mino in enumerate(my_map[self.rotation]):
            if mino:
                x = index % dimension + self.x
                y = index // dimension + self.y
                print(f'{x}, {y}')
                matrix[y][x] = self.type
        return matrix

