import pygame
from board import Board
from piece import Piece
import random

class Game:
    KEYBINDS = {
        'right': pygame.K_RIGHTBRACKET,
        'left': pygame.K_p,
        'hold': pygame.K_c,
        'cw': pygame.K_LEFTBRACKET,
        'ccw': pygame.K_z,
        '180': pygame.K_LSHIFT,
        'hd': pygame.K_SPACE,
        'sd': pygame.K_RALT
    }
    def __init__(self, window_w, window_h):
        self.w = window_w
        self.h = window_h
        self.board = Board(self.w, self.h, 300,
                           3, 4, 'black', 'white')
        self.hold = None
        self.can_hold = True
        self.queue = []
        self.generate_bag()
        self.current = Piece(self.queue[0], current=True)
        self.queue.pop(0)
        self.soft_dropping = False
        self.locked_out = False
        self.pieces = 0
        self.start_time = 0
        self.key_presses = 0
        self.lines_cleared = 0
        self.end_time = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._reset()
            if not self.locked_out:
                if event.key == Game.KEYBINDS['hold']:
                    if self.can_hold:
                        self._hold()
                        self.can_hold = False
                        self.key_presses += 1
                if event.key == Game.KEYBINDS['cw']:
                    self.current.rotation -= 1
                    self.current.collide(self.board.matrix, 'cw')
                    self.key_presses += 1
                if event.key == Game.KEYBINDS['ccw']:
                    self.current.rotation += 1
                    self.current.collide(self.board.matrix, 'ccw')
                    self.key_presses += 1
                if event.key == Game.KEYBINDS['180']:
                    self.current.rotation += 2
                    self.current.collide(self.board.matrix, '180')
                    self.key_presses += 1
                if event.key == self.KEYBINDS['sd']:
                    self.soft_dropping = True
                    self.key_presses += 1
                if event.key == Game.KEYBINDS['hd']:
                    self.drop()
                    self.board.matrix = self.current.lock_piece(self.board.matrix)
                    self.current = Piece(self.queue[0])
                    self.current.current = True
                    self.queue.pop(0)
                    if len(self.queue) < 6:
                        self.generate_bag()
                    self.can_hold = True
                    lines_cleared = self.clear_lines()
                    self.lines_cleared += lines_cleared
                    self.locked_out = self.current.test_lockout(self, self.board.matrix)
                    if self.locked_out:
                        self.final_time = pygame.time.get_ticks() - self.start_time
                    self.key_presses += 1
                    self.pieces += 1

    def _hold(self):
        if self.hold:
            temp = self.hold
            self.hold = self.current
            self.hold.reset_pos()
            self.current = temp
            self.current.current = True
        else:
            self.hold = self.current
            self.hold.reset_pos()
            self.current = Piece(self.queue[0], current=True)
            self.queue.pop(0)

    def generate_bag(self):
        bag = ['i', 'o', 'j', 'l', 's', 't', 'z']
        random.shuffle(bag)
        self.queue.extend(bag)

    def _reset(self):
        self.board.matrix = [[None for _ in range(10)] for _ in range(40)]
        self.hold = None
        self.can_hold = True
        self.queue = []
        self.generate_bag()
        self.current = Piece(self.queue[0], current=True)
        self.queue.pop(0)
        self.pieces = 0
        self.start_time = pygame.time.get_ticks()
        self.key_presses = 0
        self.lines_cleared = 0

    def drop(self):
        previous_y = None
        while not previous_y == self.current.y:
            previous_y = self.current.y
            self.current.y += 1
            self.current.collide(self.board.matrix, 'sd')

    def clear_lines(self):
        cleared_lines = 0
        for index, row in enumerate(self.board.matrix):
            # print(all(item is not None for item in row))
            if all(item is not None for item in row):
                cleared_lines += 1
                self.board.matrix.pop(index)
                self.board.matrix.insert(0, [None for _ in range(10)])

        return cleared_lines

class MovementHandler:
    DAS = 75
    ARR = 0
    def __init__(self):
        self.held_dir = None
        self.press_time = 0
        self.last_move = 0
        self.instant = (MovementHandler.ARR == 0)

    def handle_event(self, event, game):
        if not game.locked_out:
            if event.type == pygame.KEYDOWN:
                if event.key == game.KEYBINDS['left']:
                    game.current.x -= 1
                    self.held_dir = 'left'
                    self.press_time = pygame.time.get_ticks()
                    self.last_move = self.press_time
                    game.current.collide(game.board.matrix, 'left')
                    game.key_presses += 1
                elif event.key == game.KEYBINDS['right']:
                    game.current.x += 1
                    self.held_dir = 'right'
                    self.press_time = pygame.time.get_ticks()
                    self.last_move = self.press_time
                    game.current.collide(game.board.matrix, 'right')
                    game.key_presses += 1
            elif event.type == pygame.KEYUP:
                if event.key == game.KEYBINDS['sd']:
                    game.soft_dropping = False
                if event.key in (game.KEYBINDS['left'], game.KEYBINDS['right']):
                    if (event.key == game.KEYBINDS['left'] and self.held_dir == 'left') or \
                            (event.key == game.KEYBINDS['right'] and self.held_dir == 'right'):
                        self.held_dir = None

    def update(self, game):
        if game.soft_dropping:
            game.drop()
        if self.held_dir is None:
            return
        # print(self.held_dir)
        now = pygame.time.get_ticks()
        if now - self.press_time < self.DAS:
            return
        if now - self.last_move > self.ARR:
            previous_x = None
            while not previous_x == game.current.x:
                previous_x = game.current.x
                game.current.x += 1 if self.held_dir == 'right' else -1
                game.current.collide(game.board.matrix, self.held_dir)
                if game.soft_dropping:
                    game.drop()
                if not self.instant:
                    break
            self.last_move = now

