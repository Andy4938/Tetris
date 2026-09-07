import pygame
from piece import Piece

class Assets:
    def __init__(self, w, h):
        self.bg = pygame.transform.scale(pygame.image.load("bg.jpeg").convert(), (w, h))
        self.bg.set_alpha(200)
        self.skin = pygame.transform.scale(pygame.image.load("skin.png").convert(), (270, 30))
        self.ghost_skin = self.skin.copy()
        self.ghost_skin.set_alpha(150)
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
        self._draw_ghost_piece(tetris.current, board)
        self._draw_current_piece(board, tetris.current)
        self._draw_matrix(board)

    def _draw_bg(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.assets.bg, (0, 0))

    def _draw_board(self, board):
        surface = pygame.Surface((board.w + board.thickness, board.h + board.thickness), pygame.SRCALPHA)
        surface.fill(board.fill_color)
        grid_color = (107, 107, 107)
        cell_size = board.w / 10
        for row in range(1, 20):  # horizontal lines
            pygame.draw.line(surface, grid_color, (0, row * cell_size - board.thickness / 2),
                             (board.w, row * cell_size - board.thickness / 2), 2)
        for col in range(1, 10):  # vertical lines
            pygame.draw.line(surface, grid_color, (col * cell_size, 0), (col * cell_size, board.h), 2)
        # pygame.draw.rect(self.screen, 'white', (board.x - board.thickness, board.y - board.thickness, board.w + board.thickness * 2,
                                           # board.h + board.thickness * 2))  # border
        self.screen.blit(surface, (board.x, board.y))

        left_line_x = board.x - board.border_thickness / 2
        right_line_x = board.x + board.w + board.border_thickness / 2
        bottom_line_y = board.y +  20 * cell_size
        pygame.draw.line(self.screen, board.border_color, (left_line_x, board.y - board.border_thickness / 1.5),
                         (left_line_x, board.y + board.h + board.border_thickness / 2), board.border_thickness) # left border
        pygame.draw.line(self.screen, board.border_color, (right_line_x, board.y - board.border_thickness / 1.5),
                         (right_line_x, board.y + board.h + board.border_thickness / 2),
                         board.border_thickness) # right line
        pygame.draw.line(self.screen, board.border_color, (board.x, bottom_line_y),
                         (board.x + board.w, bottom_line_y), board.border_thickness) # bottom border

    def _draw_hold_box(self, board):
        hold_start_x = board.x - board.w / 2
        pygame.draw.rect(self.screen, board.border_color,
                         (hold_start_x - board.border_thickness, board.y - board.thickness, board.w / 2 + board.border_thickness,
                          board.h / 5.5 + board.border_thickness * 2))  # border
        pygame.draw.rect(self.screen, board.fill_color, (hold_start_x, board.y + 20, board.w / 2 - board.border_thickness, board.h / 5.5 - 20))
        hold_text_surface = self.assets.font.render('Hold', True, 'black')
        self.screen.blit(hold_text_surface, (hold_start_x, board.y - 2))

    def _draw_hold_piece(self, board, hold):
        x_offset = 137 if hold == 'i' else 109 if hold == 'o' else 122
        y_offset = 21 if hold == 'i' else 35
        Piece(hold).draw(self.screen, self.assets.skin, board.x - x_offset,  board.y + y_offset)

    def _draw_queue_box(self, board):
        q_start_x = board.x + board.w + board.border_thickness / 2
        pygame.draw.rect(self.screen, board.border_color, (q_start_x, board.y - board.thickness, board.w / 2 + board.border_thickness,
                                           board.h * 0.81 + board.border_thickness * 2))
        pygame.draw.rect(self.screen, board.fill_color, (q_start_x + board.border_thickness, board.y + 20, board.w / 2 - board.border_thickness, board.h * 0.81 - 20))
        next_text_surface = self.assets.font.render('Next', True, 'black')
        self.screen.blit(next_text_surface, (q_start_x + 6, board.y - 2))

    def _draw_next_pieces(self, tetris, board):
        for index, piece in enumerate(tetris.queue[:5]):
            offset = 19 if piece == 'i' else 53 if  piece == 'o' else 37
            # factor = 2 if piece == 'i' else 1
            i_offset = 16 if piece == 'i' else 0
            x = board.x + board.w + offset
            y = board.y + 40 + Piece.MINO_SIZE * index * 3 - i_offset
            Piece(piece).draw(self.screen, self.assets.skin, x, y)

    def _draw_current_piece(self, board, current):
        x = board.x + board.thickness / 3
        y = board.y - board.thickness / 3
        current.draw(self.screen, self.assets.skin, x, y)

    def _draw_matrix(self, board):
        for i, row in enumerate(board.matrix):
            for j, col in enumerate(row):
                current_mino = board.matrix[i][j]
                if current_mino:
                    crop_x = Piece.PIECES.index(current_mino) * Piece.MINO_SIZE
                    mino = pygame.Rect(crop_x, 0, Piece.MINO_SIZE, Piece.MINO_SIZE)
                    self.screen.blit(self.assets.skin, (board.x + j * Piece.MINO_SIZE + 1, board.y + (i - 20) * Piece.MINO_SIZE - 1), area=mino)

    def _draw_ghost_piece(self, current, board):
        previous_y = None
        ghost_y = current.y
        while not previous_y == ghost_y:
            previous_y = ghost_y
            ghost_y += 1
            ghost_y += current.collide(board.matrix, 'ghost', ghost_y)
        x = board.x + board.thickness / 3
        y = board.y - board.thickness / 3
        current.draw(self.screen, self.assets.ghost_skin, x, y, ghost=True, ghost_y=ghost_y)