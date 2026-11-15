import pygame
from keybinds import Keybinds

class ControlsScreen:
    HIGHLIGHT = (232, 208, 30)
    DIM = (160, 160, 160)
    MESSAGE_TIME = 2500
    BUTTONS = [('Reset to Defaults', 'reset'), ('Back', 'back')]
    # (kind, name, label) for every row above the buttons
    ROWS = [('key', action, label) for action, label in Keybinds.ACTIONS] + \
           [('handling', setting, label) for setting, label, low, high, step in Keybinds.HANDLING]

    def __init__(self, screen, window_w, window_h, keybinds):
        self.screen = screen
        self.w = window_w
        self.h = window_h
        self.keybinds = keybinds
        self.bg = pygame.transform.scale(pygame.image.load("bg.jpeg").convert(), (window_w, window_h))
        self.bg.set_alpha(200)
        self.title_font = pygame.font.Font(None, 120)
        self.header_font = pygame.font.Font(None, 48)
        self.cell_font = pygame.font.Font(None, 40)
        self.hint_font = pygame.font.Font(None, 32)

        self.label_w = 300
        self.player_w = 260
        self.panel_w = self.label_w + self.player_w * 2
        self.header_h = 50
        self.row_h = 40
        self.footer_h = 60
        self.panel_x = self.w / 2 - self.panel_w / 2
        self.panel_y = 130
        self.panel_h = self.header_h + self.row_h * len(self.ROWS) + self.footer_h + 20

        self.row = 0  # one row per entry in ROWS, the last row is the buttons
        self.col = 0  # 0 is player 1 / reset, 1 is player 2 / back
        self.waiting = False  # True while waiting for a key to bind
        self.editing = False  # True while adjusting a handling value
        self.edit_value = 0
        self.message = ''
        self.message_time = 0

    def open(self):
        self.row = 0
        self.col = 0
        self.waiting = False
        self.editing = False
        self.message = ''

    def handle_event(self, event):
        # returns 'back' when the player leaves the screen, otherwise None
        if self.waiting:
            if event.type == pygame.KEYDOWN:
                self.waiting = False
                if event.key == pygame.K_ESCAPE:
                    return None
                self._bind(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.waiting = False
            return None

        if self.editing:
            self._handle_edit_event(event)
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.row = (self.row - 1) % (len(self.ROWS) + 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.row = (self.row + 1) % (len(self.ROWS) + 1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.col = 0
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.col = 1
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self._activate()
        elif event.type == pygame.MOUSEMOTION:
            cell = self._cell_at(event.pos)
            if cell:
                self.row, self.col = cell
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cell = self._cell_at(event.pos)
            if cell:
                self.row, self.col = cell
                return self._activate()
        return None

    def _handle_edit_event(self, event):
        setting = self.ROWS[self.row][1]
        step = self._handling_info(setting)[4]
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_DOWN, pygame.K_s, pygame.K_MINUS, pygame.K_KP_MINUS):
                self._adjust(-step)
            elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_UP, pygame.K_w, pygame.K_EQUALS, pygame.K_KP_PLUS):
                self._adjust(step)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.keybinds.set_handling(self.col + 1, setting, self.edit_value)
                self._stop_editing()
            elif event.key == pygame.K_ESCAPE:
                self._stop_editing()
        elif event.type == pygame.MOUSEWHEEL:
            self._adjust(step * event.y)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.keybinds.set_handling(self.col + 1, setting, self.edit_value)
            self._stop_editing()

    def _adjust(self, amount):
        setting = self.ROWS[self.row][1]
        self.edit_value = Keybinds.clamp_handling(setting, self.edit_value + amount)

    def _stop_editing(self):
        self.editing = False
        pygame.key.set_repeat()  # turn key repeat back off so it doesn't affect the game

    def _activate(self):
        if self.row < len(self.ROWS):
            kind, name, label = self.ROWS[self.row]
            if kind == 'key':
                self.waiting = True
            else:
                self.editing = True
                self.edit_value = self.keybinds.handling[self.col + 1][name]
                pygame.key.set_repeat(300, 40)  # so holding left/right keeps adjusting
            return None
        action = self.BUTTONS[self.col][1]
        if action == 'reset':
            self.keybinds.reset()
            self._show_message('Controls reset to defaults')
            return None
        return 'back'

    def _bind(self, key):
        if key in Keybinds.RESERVED:
            self._show_message(f'{Keybinds.key_name(key)} is reserved and can\'t be bound')
            return
        player = self.col + 1
        action = self.ROWS[self.row][1]
        swapped = self.keybinds.set(player, action, key)
        if swapped:
            other_player, other_action = swapped
            label = dict(Keybinds.ACTIONS)[other_action]
            self._show_message(f'Swapped with Player {other_player} {label}')

    def _show_message(self, text):
        self.message = text
        self.message_time = pygame.time.get_ticks()

    @staticmethod
    def _handling_info(setting):
        for info in Keybinds.HANDLING:
            if info[0] == setting:
                return info

    def _cell_rect(self, row, col):
        if row < len(self.ROWS):
            x = self.panel_x + self.label_w + col * self.player_w
            y = self.panel_y + self.header_h + row * self.row_h
            return pygame.Rect(x, y, self.player_w, self.row_h)
        button_w = self.panel_w / 2
        y = self.panel_y + self.header_h + len(self.ROWS) * self.row_h + 10
        return pygame.Rect(self.panel_x + col * button_w, y, button_w, self.footer_h)

    def _cell_at(self, pos):
        for row in range(len(self.ROWS) + 1):
            for col in range(2):
                if self._cell_rect(row, col).collidepoint(pos):
                    return row, col
        return None

    def draw(self):
        self.screen.fill((100, 100, 100))
        self.screen.blit(self.bg, (0, 0))

        title_surface = self.title_font.render('CONTROLS', True, 'white')
        self.screen.blit(title_surface, title_surface.get_rect(center=(self.w / 2, 70)))

        panel = pygame.Surface((self.panel_w, self.panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 200))
        self.screen.blit(panel, (self.panel_x, self.panel_y))
        pygame.draw.rect(self.screen, 'white', (self.panel_x, self.panel_y, self.panel_w, self.panel_h), 4)

        self._draw_headers()
        self._draw_rows()
        self._draw_buttons()
        self._draw_footer_text()

    def _draw_divider(self, y):
        pygame.draw.line(self.screen, (107, 107, 107), (self.panel_x + 10, y), (self.panel_x + self.panel_w - 10, y), 2)

    def _draw_headers(self):
        for col, header in enumerate(('Player 1', 'Player 2')):
            x = self.panel_x + self.label_w + col * self.player_w + self.player_w / 2
            header_surface = self.header_font.render(header, True, 'white')
            self.screen.blit(header_surface, header_surface.get_rect(center=(x, self.panel_y + self.header_h / 2 + 4)))
        self._draw_divider(self.panel_y + self.header_h)

    def _draw_rows(self):
        for row, (kind, name, label) in enumerate(self.ROWS):
            y = self.panel_y + self.header_h + row * self.row_h
            if kind == 'handling' and self.ROWS[row - 1][0] == 'key':
                self._draw_divider(y)  # separates the keybinds from the handling settings
            label_surface = self.cell_font.render(label, True, 'white')
            self.screen.blit(label_surface, label_surface.get_rect(midleft=(self.panel_x + 30, y + self.row_h / 2)))
            for col in range(2):
                rect = self._cell_rect(row, col)
                selected = (row, col) == (self.row, self.col)
                if selected:
                    self._draw_highlight(rect)
                text, color = self._cell_text(kind, name, col, selected)
                text_surface = self.cell_font.render(text, True, color)
                self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def _cell_text(self, kind, name, col, selected):
        color = self.HIGHLIGHT if selected else self.DIM
        if kind == 'key':
            if selected and self.waiting:
                return 'Press a key...', self.HIGHLIGHT
            return Keybinds.key_name(self.keybinds.binds[col + 1][name]), color
        if selected and self.editing:
            return f'<  {self.edit_value} ms  >', self.HIGHLIGHT
        return f'{self.keybinds.handling[col + 1][name]} ms', color

    def _draw_buttons(self):
        for col, (label, action) in enumerate(self.BUTTONS):
            rect = self._cell_rect(len(self.ROWS), col)
            selected = (len(self.ROWS), col) == (self.row, self.col)
            if selected:
                self._draw_highlight(rect)
            text_surface = self.header_font.render(label, True, self.HIGHLIGHT if selected else 'white')
            self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def _draw_highlight(self, rect):
        highlight = pygame.Surface((rect.w - 8, rect.h - 4), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 40))
        self.screen.blit(highlight, (rect.x + 4, rect.y + 2))

    def _draw_footer_text(self):
        if self.message and pygame.time.get_ticks() - self.message_time < self.MESSAGE_TIME:
            message_surface = self.header_font.render(self.message, True, self.HIGHLIGHT)
            self.screen.blit(message_surface, message_surface.get_rect(center=(self.w / 2, self.panel_y + self.panel_h + 35)))
        if self.waiting:
            hint = 'Press the new key    Esc to cancel'
        elif self.editing:
            setting = self.ROWS[self.row][1]
            hint = f'{self._handling_description(setting)}    Left / Right to adjust    Enter to save    Esc to cancel'
        else:
            hint = 'Arrow keys / mouse to select    Enter to change    Esc to go back'
        hint_surface = self.hint_font.render(hint, True, 'white')
        self.screen.blit(hint_surface, hint_surface.get_rect(center=(self.w / 2, self.h - 30)))

    @staticmethod
    def _handling_description(setting):
        if setting == 'das':
            return 'DAS: how long to hold before the piece starts sliding'
        return 'ARR: time between each step of the slide (0 = instant)'
