import pygame
from piece import Piece

class Assets:
    def __init__(self, w, h):
        self.bg = pygame.transform.scale(pygame.image.load("bg.jpeg").convert(), (w, h))
        self.bg.set_alpha(200)
        self.skin = pygame.transform.scale(pygame.image.load("skin.png").convert(), (270, 30))
        self.font = pygame.font.Font(None, 32)

class Renderer:
    def __init__(self, screen, window_w, window_h):
        self.screen = screen
        self.assets = Assets(window_w, window_h)

    def draw_game(self, tetris):
        board = tetris.board
        self._draw_bg()
        self._draw_board(board)
        self._draw_hold_box(board)
        if tetris.hold:
            self._draw_hold_piece(board, tetris.hold.type)
        self._draw_queue_box(board)
        self._draw_next_pieces(tetris, board)
        self._draw_current_piece(board, tetris.current)

    def _draw_bg(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.assets.bg, (0, 0))

    def _draw_board(self, board):
        surface = pygame.Surface((board.w, board.h), pygame.SRCALPHA)
        surface.fill(board.fill_color)
        grid_color = (107, 107, 107)
        cell_size = board.w / 10
        for row in range(1, 20):  # horizontal lines
            pygame.draw.line(surface, grid_color, (0, row * cell_size), (board.w, row * cell_size), 2)

        for col in range(1, 10):  # vertical lines
            pygame.draw.line(surface, grid_color, (col * cell_size, 0), (col * cell_size, board.h), 2)
        pygame.draw.rect(self.screen, 'white', (board.x - board.thickness, board.y - board.thickness, board.w + board.thickness * 2,
                                           board.h + board.thickness * 2))  # border
        self.screen.blit(surface, (board.x, board.y))

    def _draw_hold_box(self, board):
        hold_start_x = board.x - board.w / 2
        pygame.draw.rect(self.screen, 'white',
                         (hold_start_x - board.thickness * 2, board.y - board.thickness, board.w / 2 + board.thickness * 2,
                          board.h / 5.5 + board.thickness * 2))  # border
        pygame.draw.rect(self.screen, board.fill_color, (hold_start_x - board.thickness, board.y + 20, board.w / 2, board.h / 5.5 - 20))
        hold_text_surface = self.assets.font.render('Hold', True, 'black')
        self.screen.blit(hold_text_surface, (hold_start_x, board.y - 2))

    def _draw_hold_piece(self, board, hold):
        x_offset = 137 if hold == 'i' or hold == 'o' else 122
        y_offset = 21 if hold == 'i' else 35
        Piece(hold).draw(self.screen, self.assets.skin, board.x - x_offset, board.y + y_offset)

    def _draw_queue_box(self, board):
        q_start_x = board.x + board.w
        pygame.draw.rect(self.screen, 'white', (q_start_x, board.y - board.thickness, board.w / 2 + board.thickness * 2,
                                           board.h * 0.81 + board.thickness * 2))
        pygame.draw.rect(self.screen, 'black', (q_start_x + board.thickness, board.y + 20, board.w / 2, board.h * 0.81 - 20))
        next_text_surface = self.assets.font.render('Next', True, 'black')
        self.screen.blit(next_text_surface, (q_start_x + 6, board.y - 2))

    def _draw_next_pieces(self, tetris, board):
        for index, piece in enumerate(tetris.queue[:5]):
            offset = 18 if piece == 'i' or piece == 'o' else 34
            # factor = 2 if piece == 'i' else 1
            i_offset = 16 if piece == 'i' else 0
            x = board.x + board.w + offset
            y = board.y + 40 + Piece.MINO_SIZE * index * 3 - i_offset
            Piece(piece).draw(self.screen, self.assets.skin, x, y)

    def _draw_current_piece(self, board, current):
        x = board.x + Piece.MINO_SIZE * 3 + 1
        y = board.y - Piece.MINO_SIZE * 3 + 1
        current.draw(self.screen, self.assets.skin, x, y)
