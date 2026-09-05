import pygame
from render import Renderer
from game import Game

pygame.init()
WINDOW_W = 1366
WINDOW_H = 768
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
clock = pygame.time.Clock()
running = True
tetris = Game(WINDOW_W, WINDOW_H)
renderer = Renderer(screen, WINDOW_W, WINDOW_H)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        tetris.handle_event(event)
    renderer.draw_game(tetris)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
