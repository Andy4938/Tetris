import pygame
from piece import Piece

class Menu:
    TITLE = 'TETRIS'
    TITLE_PIECES = ['z', 'l', 'o', 's', 'i', 't']  # colors each title letter with a mino color from the skin
    HIGHLIGHT = (232, 208, 30)
    DISABLED = (120, 120, 120)

    def __init__(self, screen, window_w, window_h):
        self.screen = screen
        self.w = window_w
        self.h = window_h
        self.bg = pygame.transform.scale(pygame.image.load("bg.jpeg").convert(), (window_w, window_h))
        self.bg.set_alpha(200)
        self.skin = pygame.transform.scale(pygame.image.load("skin.png").convert(), (252, 28))
        self.title_font = pygame.font.Font(None, 200)
        self.option_font = pygame.font.Font(None, 64)
        self.hint_font = pygame.font.Font(None, 32)
        # (label, action, enabled)
        self.options = [
            ('Sprint', 'sprint', True),
            ('Versus', 'versus', True),
            ('Controls', 'controls', True),
            ('Quit', 'quit', True)
        ]
        self.selected = 0
        self.option_rects = []
        self.panel_w = 420
        self.option_h = 80
        self.panel_x = self.w / 2 - self.panel_w / 2
        self.panel_y = self.h / 2 - 40

    def handle_event(self, event):
        # returns the action of the chosen option, or None
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move_selection(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._move_selection(1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self._choose(self.selected)
            elif event.key == pygame.K_ESCAPE:
                return 'quit'
        elif event.type == pygame.MOUSEMOTION:
            index = self._option_at(event.pos)
            if index is not None and self.options[index][2]:
                self.selected = index
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self._option_at(event.pos)
            if index is not None:
                return self._choose(index)
        return None

    def _move_selection(self, step):
        index = self.selected
        for _ in range(len(self.options)):
            index = (index + step) % len(self.options)
            if self.options[index][2]:
                self.selected = index
                return

    def _choose(self, index):
        label, action, enabled = self.options[index]
        return action if enabled else None

    def _option_at(self, pos):
        for index, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                return index
        return None

    def draw(self):
        self.screen.fill((100, 100, 100))
        self.screen.blit(self.bg, (0, 0))
        self._draw_title()
        self._draw_options()
        self._draw_hint()

    def _draw_title(self):
        letters = []
        for index, letter in enumerate(self.TITLE):
            crop_x = Piece.PIECES.index(self.TITLE_PIECES[index]) * Piece.MINO_SIZE
            color = self.skin.get_at((crop_x + Piece.MINO_SIZE // 2, Piece.MINO_SIZE // 2))
            letters.append(self.title_font.render(letter, True, color))
        spacing = 8
        total_w = sum(letter.get_width() for letter in letters) + spacing * (len(letters) - 1)
        x = self.w / 2 - total_w / 2
        y = self.h / 5
        for letter in letters:
            shadow = letter.copy()
            shadow.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MIN)
            self.screen.blit(shadow, (x + 6, y + 6))
            self.screen.blit(letter, (x, y))
            x += letter.get_width() + spacing

    def _draw_options(self):
        panel_h = self.option_h * len(self.options) + 20
        panel = pygame.Surface((self.panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 200))
        self.screen.blit(panel, (self.panel_x, self.panel_y))
        pygame.draw.rect(self.screen, 'white', (self.panel_x, self.panel_y, self.panel_w, panel_h), 4)

        self.option_rects = []
        for index, (label, action, enabled) in enumerate(self.options):
            rect = pygame.Rect(self.panel_x, self.panel_y + 10 + index * self.option_h, self.panel_w, self.option_h)
            self.option_rects.append(rect)
            selected = index == self.selected
            if selected:
                highlight = pygame.Surface((rect.w - 8, rect.h), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 40))
                self.screen.blit(highlight, (rect.x + 4, rect.y))
            color = self.HIGHLIGHT if selected else 'white' if enabled else self.DISABLED
            text_surface = self.option_font.render(label, True, color)
            if enabled:
                self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))
            else:
                self.screen.blit(text_surface, text_surface.get_rect(center=(rect.centerx, rect.centery - 12)))
                soon_surface = self.hint_font.render('Coming soon', True, self.DISABLED)
                self.screen.blit(soon_surface, soon_surface.get_rect(center=(rect.centerx, rect.centery + 22)))
            if selected:
                # t mino as the cursor
                crop_x = Piece.PIECES.index('t') * Piece.MINO_SIZE
                mino = pygame.Rect(crop_x, 0, Piece.MINO_SIZE, Piece.MINO_SIZE)
                self.screen.blit(self.skin, (rect.x + 30, rect.centery - Piece.MINO_SIZE / 2), area=mino)

    def _draw_hint(self):
        hint = 'Arrow keys / mouse to select    Enter to start    Esc in game to return here'
        hint_surface = self.hint_font.render(hint, True, 'white')
        self.screen.blit(hint_surface, hint_surface.get_rect(center=(self.w / 2, self.h - 30)))
