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

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == Game.KEYBINDS['hold']:
                if self.can_hold:
                    self._hold()
                    self.can_hold = False
            if event.key == pygame.K_r:
                self.board.matrix = [[None for _ in range(10)] for _ in range(40)]
                self.hold = None
                self.can_hold = True
                self.queue = []
                self.generate_bag()
                self.current = Piece(self.queue[0], current=True)
                self.queue.pop(0)
            if event.key == Game.KEYBINDS['right']:
                self.current.x += 1
                self.current.collide(self.board.matrix, 'right')
            if event.key == Game.KEYBINDS['left']:
                self.current.x -= 1
                self.current.collide(self.board.matrix, 'left')
            if event.key == Game.KEYBINDS['sd']:
                self.current.y += 1
                self.current.collide(self.board.matrix, 'sd')
            if event.key == Game.KEYBINDS['hd']:
                previous_y = None
                while not previous_y == self.current.y:
                    previous_y = self.current.y
                    self.current.y += 1
                    self.current.collide(self.board.matrix, 'sd')
                self.board.matrix = self.current.lock_piece(self.board.matrix)
                self.current = Piece(self.queue[0])
                self.current.current = True
                self.queue.pop(0)
                if len(self.queue) < 6:
                    self.generate_bag()
                self.can_hold = True

    def _hold(self):
        if self.hold:
            temp = self.hold
            self.hold = self.current
            self.current = temp
            self.current.current = True
        else:
            self.hold = self.current
            self.current = Piece(self.queue[0], current=True)
            self.queue.pop(0)

    def generate_bag(self):
        bag = ['i', 'o', 'j', 'l', 's', 't', 'z']
        random.shuffle(bag)
        self.queue.extend(bag)
