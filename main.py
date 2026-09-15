import pygame
from render import Renderer
from game import Game, MovementHandler, SharedQueue

pygame.init()
WINDOW_W = 1366
WINDOW_H = 768
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
clock = pygame.time.Clock()
running = True
mode = 'versus'
queue = SharedQueue()
tetris_p1 = Game(WINDOW_W, WINDOW_H, WINDOW_W / 2.5, 1, mode, queue)
renderer1 = Renderer(screen, WINDOW_W, WINDOW_H)
input_handler1 = MovementHandler()
if mode == 'versus':
    tetris_p1 = Game(WINDOW_W, WINDOW_H, WINDOW_W / 5.95, 1, mode, queue)
    tetris_p2 = Game(WINDOW_W, WINDOW_H, WINDOW_W / 1.55, 2, mode, queue, tetris_p1)
    tetris_p1.opponent = tetris_p2
    renderer1 = Renderer(screen, WINDOW_W, WINDOW_H)
    renderer2 = Renderer(screen, WINDOW_W, WINDOW_H)
    input_handler1 = MovementHandler()
    input_handler2 = MovementHandler()

while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            tetris_p1.handle_event(event)
            input_handler1.handle_event(event, tetris_p1)

            if mode == 'versus':
                tetris_p2.handle_event(event)
                input_handler2.handle_event(event, tetris_p2)
        input_handler1.update(tetris_p1)
        renderer1.draw_bg()
        renderer1.draw_game(tetris_p1)

        if mode == 'versus':
            input_handler2.update(tetris_p2)
            renderer2.draw_game(tetris_p2)
        pygame.display.flip()
        clock.tick(240)


pygame.quit()
