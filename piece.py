import pygame
import render

class Piece:
    PIECES = ['p', 'g', 'z', 'l', 'o', 's', 'i', 'j', 't']
    MINO_SIZE = 30
    MINO_MAPS = {
        # represents filled in minos of a 3x2 grid, except I and O in a 4x2
        'z': [1, 1, 0, 0, 1, 1],
        'l': [0, 0, 1, 1, 1, 1],
        's': [0, 1, 1, 1, 1, 0],
        'j': [1, 0, 0, 1, 1, 1],
        't': [0, 1, 0, 1, 1, 1],
        'i': [0, 0, 0, 0, 1, 1, 1, 1],
        'o': [0, 1, 1, 0, 0, 1, 1, 0],
    }
    def __init__(self, type, rotation=0):
        self.type = type
        self.rotation = rotation

    def draw(self, screen, skin, x, y):
        crop_x = Piece.PIECES.index(self.type) * Piece.MINO_SIZE
        mino = pygame.Rect(crop_x, 0, Piece.MINO_SIZE, Piece.MINO_SIZE)
        mino_map = Piece.MINO_MAPS[self.type]
        dimension = int(len(mino_map) / 2)
        for i in range(2):
            y_pos = i * Piece.MINO_SIZE
            for j in range(dimension):
                x_pos = j * Piece.MINO_SIZE
                if mino_map[i * dimension + j] == 1:
                    screen.blit(skin, (x + x_pos, y + y_pos), area=mino)