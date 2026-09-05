import pygame
from board import Board
from piece import Piece
import random

class Game:
    def __init__(self, window_w, window_h):
        self.w = window_w
        self.h = window_h
        self.board = Board(self.w, self.h, 300,
                           3, 'black', 'white')
        self.hold = None
        self.can_hold = True
        self.queue = []
        self.generate_bag()
        self.current = Piece(self.queue[0])
        self.queue.pop(0)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                if self.can_hold:
                    self._hold()
                    self.can_hold = False

    def _hold(self):
        if self.hold:
            temp = self.hold
            self.hold = self.current
            self.current = temp
        else:
            self.hold = self.current
            self.current = Piece(self.queue[0])
            self.queue.pop(0)

    def generate_bag(self):
        bag = ['i', 'o', 'j', 'l', 's', 't', 'z']
        random.shuffle(bag)
        self.queue.extend(bag)
