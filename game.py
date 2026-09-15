import pygame
from board import Board
from piece import Piece
import random

class Game:
    SPINS = ['', 'Single', 'Double', 'Triple', 'Tetris']
    def __init__(self, window_w, window_h, x, player, mode, queue, opponent=None):
        self.w = window_w
        self.h = window_h
        self.board = Board(self.w, self.h, x, 280,
                           3, 4, 'black', 'white')
        self.hold = None
        self.can_hold = True
        self.queue = queue
        self.current = Piece(self.queue.pieces[0], current=True)
        self.queue_pos = 1
        self.soft_dropping = False
        self.locked_out = False
        self.pieces = 0
        self.reset_time = 0
        self.start_time = 0
        self.key_presses = 0
        self.lines_cleared = 0
        self.end_time = 0
        self.resetting = True
        self.reset_animation_done = False
        self.spin_type = ''
        self.last_input = None
        self.force_spin = False
        self.player = player
        self.last_lines_cleared = 0
        self.mode = mode
        self.garbage = []
        self.opponent = opponent
        self.combo = 0
        self.b2b = 0
        self.attack = 0
        self.last_attack = 0

        if player == 1:
            self.KEYBINDS = {
                'right': pygame.K_RIGHTBRACKET,
                'left': pygame.K_p,
                'hold': pygame.K_c,
                'cw': pygame.K_LEFTBRACKET,
                'ccw': pygame.K_z,
                '180': pygame.K_LSHIFT,
                'hd': pygame.K_SPACE,
                'sd': pygame.K_RALT
            }
        else:
            self.KEYBINDS = {
                'right': pygame.K_RIGHTBRACKET,
                'left': pygame.K_p,
                'hold': pygame.K_c,
                'cw': pygame.K_LEFTBRACKET,
                'ccw': pygame.K_z,
                '180': pygame.K_LSHIFT,
                'hd': pygame.K_SPACE,
                'sd': pygame.K_RALT
            }

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and self.reset_animation_done:
                self._reset()
            if not self.locked_out and not self.resetting:
                if event.key == self.KEYBINDS['hold']:
                    self.key_presses += 1
                    if self.can_hold:
                        self._hold()
                        self.can_hold = False
                        self.last_input = 'hold'
                if event.key == self.KEYBINDS['cw']:
                    self.current.rotation -= 1
                    self.force_spin, failed = self.current.collide(self.board.matrix, 'cw')
                    self.key_presses += 1
                    if not failed:
                        self.last_input = 'cw'
                if event.key == self.KEYBINDS['ccw']:
                    self.current.rotation += 1
                    self.force_spin, failed = self.current.collide(self.board.matrix, 'ccw')
                    self.key_presses += 1
                    if not failed:
                        self.last_input = 'ccw'
                if event.key == self.KEYBINDS['180']:
                    self.current.rotation += 2
                    failed = self.current.collide(self.board.matrix, '180')
                    self.key_presses += 1
                    if not failed:
                        self.last_input = '180'
                if event.key == self.KEYBINDS['sd']:
                    self.soft_dropping = True
                    self.key_presses += 1
                if event.key == self.KEYBINDS['hd']:
                    self.drop()
                    self.board.matrix, self.spin_type = self.current.lock_piece(self.board.matrix)
                    self.current = Piece(self.queue.pieces[self.queue_pos])
                    self.current.current = True
                    self.queue_pos += 1
                    if len(self.queue.pieces) - self.queue_pos < 6:
                        self.queue.generate_bag()
                    self.can_hold = True
                    self.last_lines_cleared = self.clear_lines()
                    # if self.spin_type != 'none' and self.last_lines_cleared > 0:
                        # self.spin_type = f'{self.spin_type}'
                    if self.force_spin and self.spin_type[:4] == 'Mini':
                        self.spin_type = self.spin_type[4:]
                    if not (self.last_input in ('cw', 'ccw', '180')):
                        self.spin_type = ''
                    # if self.player == 1:
                        # print(self.last_input)
                    self.lines_cleared += self.last_lines_cleared
                    self.locked_out = self.current.test_lockout(self, self.board.matrix)
                    if self.locked_out:
                        self.final_time = pygame.time.get_ticks() - self.start_time
                    self.key_presses += 1
                    # self.last_input = 'hd'
                    self.pieces += 1
                    if self.last_lines_cleared > 0:
                        print(self.spin_type)
                        self.last_attack = self.calculate_attack(self.last_lines_cleared, self.spin_type)
                        self.attack += self.last_attack
                        self.combo += 1
                        print(self.combo)
                    else:
                        self.combo = 0
                        self.last_attack = 0
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
            self.current = Piece(self.queue.pieces[self.queue_pos], current=True)
            self.queue_pos += 1

    def generate_bag(self):
        bag = ['i', 'o', 'j', 'l', 's', 't', 'z']
        random.shuffle(bag)
        self.queue.extend(bag)

    def _reset(self):
        self.resetting = True
        self.board.matrix = [[None for _ in range(10)] for _ in range(40)]
        self.hold = None
        self.can_hold = True
        if self.player == 1:
            self.queue.reset()
        self.current = Piece(self.queue.pieces[0], current=True)
        self.queue_pos = 1
        self.locked_out = False
        self.pieces = 0
        self.reset_time = pygame.time.get_ticks()
        self.start_time = pygame.time.get_ticks()
        self.key_presses = 0
        self.lines_cleared = 0
        self.reset_animation_done = False
        self.spin_type = ''
        self.last_input = None
        self.force_spin = False
        self.last_lines_cleared = 0
        self.garbage = []
        self.combo = 0
        self.b2b = 0
        self.attack = 0

    def drop(self):
        previous_y = None
        while not previous_y == self.current.y:
            previous_y = self.current.y
            self.current.y += 1
            self.current.collide(self.board.matrix, 'sd')
            # print(previous_y)
            # print(self.current.y)
            if previous_y != self.current.y:
                self.last_input = 'sd'
                # print('hi')

    def clear_lines(self):
        cleared_lines = 0
        for index, row in enumerate(self.board.matrix):
            # print(all(item is not None for item in row))
            if all(item is not None for item in row):
                cleared_lines += 1
                self.board.matrix.pop(index)
                self.board.matrix.insert(0, [None for _ in range(10)])

        return cleared_lines

    def calculate_attack(self, lines, clear):
        base = [0, 0, 1, 2, 4]
        base_spin = [0, 2, 4, 6]
        combo_table = []
        attack = base_spin[lines] if clear == 'T-spin' else base[lines]
        attack += int(self.combo // (1 + self.combo / 5) * (1 + attack))
        if 'spin' in clear and self.b2b > 0:
            attack += 1
        self.b2b = self.b2b + 1 if 'spin' in clear or lines == 4 else 0
        return attack

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
                    if not game.resetting:
                        game.current.x -= 1
                    self.held_dir = 'left'
                    self.press_time = pygame.time.get_ticks()
                    self.last_move = self.press_time
                    game.last_input = 'left' if game.current.collide(game.board.matrix, 'left') else game.last_input
                    game.key_presses += 1
                elif event.key == game.KEYBINDS['right']:
                    if not game.resetting:
                        game.current.x += 1
                    self.held_dir = 'right'
                    self.press_time = pygame.time.get_ticks()
                    self.last_move = self.press_time
                    game.last_input = 'right' if game.current.collide(game.board.matrix, 'right') else game.last_input
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
                if not game.resetting:
                    game.current.x += 1 if self.held_dir == 'right' else -1
                game.current.collide(game.board.matrix, self.held_dir)
                if game.soft_dropping:
                    game.drop()
                if not self.instant:
                    break
            self.last_move = now

class SharedQueue:
    def __init__(self):
        self.pieces = []
        self.generate_bag()

    def generate_bag(self):
        bag = ['i', 'o', 'j', 'l', 's', 't', 'z']
        random.shuffle(bag)
        self.pieces.extend(bag)

    def reset(self):
        self.pieces = []
        self.generate_bag()