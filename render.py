import pygame
from piece import Piece

class Assets:
    def __init__(self, w, h):
        self.bg = pygame.transform.scale(pygame.image.load("bg.jpeg").convert(), (w, h))
        self.bg.set_alpha(200)
        self.skin = pygame.transform.scale(pygame.image.load("skin.png").convert(), (252, 28))
        self.ghost_skin = self.skin.copy()
        self.ghost_skin.set_alpha(150)
        self.font = pygame.font.Font(None, 32)
        self.stat_label_font = pygame.font.Font(None, 48)
        self.stat_font = pygame.font.Font(None, 48)
        self.lines_left_font = pygame.font.Font(None, 200)
        self.reset_scales = [1.5, 1.5, 1.5] # 0 is ready, 1 is set, 2 is go
        self.reset_alphas = [0, 0, 0]

class Renderer:
    def __init__(self, screen, window_w, window_h):
        self.screen = screen
        self.assets = Assets(window_w, window_h)

    def draw_game(self, tetris):
        board = tetris.board
        self._draw_board(board)
        self._draw_hold_box(board)
        if tetris.hold:
            self._draw_hold_piece(board, tetris.hold.type)
        self._draw_queue_box(board)
        self._draw_next_pieces(tetris, board)
        self._draw_ghost_piece(tetris.current, board)
        self._draw_current_piece(board, tetris.current)
        self._draw_matrix(board)
        self._display_stats(tetris)
        if not tetris.reset_animation_done:
            self._new_game(tetris)

    def draw_bg(self):
        self.screen.fill((100, 100, 100))
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
        x_offset = 128 if hold == 'i' else 100 if hold == 'o' else 113
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
            offset = 18.5 if piece == 'i' else 47 if  piece == 'o' else 34
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

    def _display_stats(self, game):
        stat_y_start = game.board.y + game.board.h / 3
        stat_x_start = game.board.x - 10
        # Pieces
        self._display_stat('Pieces', stat_x_start - 130, stat_y_start, is_label=True)
        self._display_stat(str(game.pieces), stat_x_start - 40 - 19 * (len(str(game.pieces)) - 1), stat_y_start + 40)
        # Time
        time_raw = game.final_time if game.locked_out else pygame.time.get_ticks() - game.start_time
        hours = '' if time_raw < 3600000 else time_raw // 3600000
        minutes = (time_raw // 60000) % 60
        minutes_display = '00' if minutes < 1 else f'0{minutes}' if minutes < 10 else minutes
        seconds = (time_raw // 1000) % 60
        seconds_display = '00' if seconds < 1 else f'0{seconds}' if seconds < 10 else seconds
        ms = time_raw % 1000
        ms_display = f'00{ms}' if ms < 10 else f'0{ms}' if ms < 100 else ms
        time = '00:00.000' if game.resetting else f'{minutes_display}:{seconds_display}.{ms_display}'
        self._display_stat('Time', stat_x_start - 100, stat_y_start + 300, is_label=True)
        self._display_stat(time, stat_x_start - 23 - 19 * (len(time) - 1), stat_y_start + 340)
        # PPS
        pps = f'{round(game.pieces / time_raw * 1000, 2):.2f}'
        self._display_stat('PPS', stat_x_start - 90, stat_y_start + 100, is_label=True)
        self._display_stat(pps, stat_x_start - 30 - 19 * (len(pps) - 1), stat_y_start + 140)
        # KPP
        kpp = '0.00' if game.pieces == 0 else f'{round(game.key_presses / game.pieces, 2):.2f}'
        self._display_stat('KPP', stat_x_start - 90, stat_y_start + 200, is_label=True)
        self._display_stat(kpp, stat_x_start - 30 - 19 * (len(kpp) - 1), stat_y_start + 240)
        # Lines
        lines = str(game.lines_cleared)
        self._display_stat('Lines', game.board.x + game.board.w + 35, stat_y_start + 290, is_label=True)
        self._display_stat(lines, game.board.x + game.board.w + 65 - 8 * (len(lines) - 1), stat_y_start + 330)
        # Lines left
        lines_left = '0' if game.lines_cleared > 40 else str(40 - game.lines_cleared)
        lines_left_surface = self.assets.lines_left_font.render(lines_left, True,
                                                          (255, 255, 255))
        lines_left_surface.set_alpha((100))
        self.screen.blit(lines_left_surface, (game.board.x + game.board.w / 2.5 - 50 * (len(lines_left) - 1), game.board.y + game.board.h / 8))
        # Spin
        if game.spin_type != '' or game.last_lines_cleared > 0:
            self._display_stat(f'{game.spin_type} {game.SPINS[game.last_lines_cleared]}', game.board.x + game.board.w / 2 - 9 * (len(str(game.spin_type)) + len(game.SPINS[game.last_lines_cleared])), game.board.y + game.board.h + 20)

    def _display_stat(self, text, x, y, is_label=False):
        text_surface = self.assets.stat_label_font.render(text, True, 'white') if is_label else self.assets.stat_font.render(text, True, 'white')
        self.screen.blit(text_surface, (x, y))

    def _new_game(self, game):
        time = pygame.time.get_ticks() - game.reset_time
        # text_surface = self.assets.lines_left_font.render('Ready', True, (232, 208, 30))
        # orig_w, orig_h = text_surface.get_size()
        # scale = self.assets.reset_scales[0]
        # self.assets.reset_scales[0] -= ((scale - 0.5) / 10)
        # scaled_surface = pygame.transform.smoothscale(text_surface, (orig_w * scale, orig_h * scale))
        # scaled_surface.set_alpha(self.assets.reset_alphas[0])
        # self.assets.reset_alphas[0] += 20 if time < 700 else self.assets.reset_alphas[0] / -20
        # self.screen.blit(scaled_surface, ((game.board.x + game.board.w / 2 - scale * 210), game.board.y + game.board.h / 3))
        self._fading_text(time, 0, 250, 'READY', 0, (game.board.x + game.board.w / 2), game.board.y + game.board.h / 2.5)
        self._fading_text(time, 500, 750, 'SET', 1, (game.board.x + game.board.w / 2 + 6), game.board.y + game.board.h / 2.5)
        self._fading_text(time, 1000, 1250, 'GO!', 2, (game.board.x + game.board.w / 2 + 10), game.board.y + game.board.h / 2.5)
        if time > 1000 and game.resetting:
            game.resetting = False
            game.start_time = pygame.time.get_ticks()
        if time > 2000:
            game.reset_animation_done = True
            self.assets.reset_scales = [1.5, 1.5, 1.5]  # 0 is ready, 1 is set, 2 is go
            self.assets.reset_alphas = [0, 0, 0]

    def _fading_text(self, time, starting_time, disappearing_time, text, order, x, y):
        if time > starting_time:
            text_surface = self.assets.lines_left_font.render(text, True, (232, 208, 30))
            orig_w, orig_h = text_surface.get_size()
            scale = self.assets.reset_scales[order]
            self.assets.reset_scales[order] -= ((scale - 0.5) / 10)
            scaled_surface = pygame.transform.smoothscale(text_surface, (orig_w * scale, orig_h * scale))
            scaled_surface.set_alpha(self.assets.reset_alphas[order])
            self.assets.reset_alphas[order] += 20 if time < disappearing_time else -10
            self.screen.blit(scaled_surface,
                             (x - scale * len(text) * 48, y))