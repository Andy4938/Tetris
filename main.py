import pygame
from render import Renderer
from game import Game, MovementHandler

pygame.init()
WINDOW_W = 1366
WINDOW_H = 768
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
clock = pygame.time.Clock()
running = True
tetris_p1 = Game(WINDOW_W, WINDOW_H, WINDOW_W / 6, 1)
tetris_p2 = Game(WINDOW_W, WINDOW_H, WINDOW_W / 1.6, 2)
renderer1 = Renderer(screen, WINDOW_W, WINDOW_H)
renderer2 = Renderer(screen, WINDOW_W, WINDOW_H)
input_handler1 = MovementHandler()
input_handler2 = MovementHandler()
mode = 'sprint'

while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            tetris_p1.handle_event(event)
            input_handler1.handle_event(event, tetris_p1)
            tetris_p2.handle_event(event)
            input_handler2.handle_event(event, tetris_p2)
        input_handler1.update(tetris_p1)
        input_handler2.update(tetris_p2)

        renderer1.draw_bg()
        renderer1.draw_game(tetris_p1)
        renderer2.draw_game(tetris_p2)
        pygame.display.flip()
        clock.tick(240)


pygame.quit()
