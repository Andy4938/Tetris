import pygame
from render import Renderer
from game import Game, MovementHandler, SharedQueue
from menu import Menu
from controls import ControlsScreen
from keybinds import Keybinds

pygame.init()
WINDOW_W = 1366
WINDOW_H = 768
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()
running = True
state = 'menu'
mode = None
menu = Menu(screen, WINDOW_W, WINDOW_H)
keybinds = Keybinds()
controls = ControlsScreen(screen, WINDOW_W, WINDOW_H, keybinds)

def start_game(mode):
    # builds fresh games, renderers and input handlers for the chosen mode
    queue = SharedQueue()
    if mode == 'versus':
        tetris_p1 = Game(WINDOW_W, WINDOW_H, WINDOW_W / 5.95, 1, mode, queue, keybinds=keybinds.get(1))
        tetris_p2 = Game(WINDOW_W, WINDOW_H, WINDOW_W / 1.55, 2, mode, queue, keybinds=keybinds.get(2))
        tetris_p1.opponent = tetris_p2
        tetris_p2.opponent = tetris_p1
        games = [tetris_p1, tetris_p2]
    else:
        games = [Game(WINDOW_W, WINDOW_H, WINDOW_W / 2.5, 1, mode, queue, keybinds=keybinds.get(1))]
    for game in games:
        game.reset_time = pygame.time.get_ticks()  # so the ready/set/go countdown starts now, not at program launch
    renderers = [Renderer(screen, WINDOW_W, WINDOW_H) for _ in games]
    input_handlers = []
    for game in games:
        handling = keybinds.get_handling(game.player)
        input_handlers.append(MovementHandler(handling['das'], handling['arr']))
    return games, renderers, input_handlers

while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif state == 'menu':
                action = menu.handle_event(event)
                if action == 'quit':
                    running = False
                elif action in ('sprint', 'versus'):
                    mode = action
                    games, renderers, input_handlers = start_game(mode)
                    state = 'game'
                elif action == 'controls':
                    controls.open()
                    state = 'controls'
            elif state == 'controls':
                if controls.handle_event(event) == 'back':
                    state = 'menu'
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = 'menu'
            else:
                for game, input_handler in zip(games, input_handlers):
                    game.handle_event(event)
                    input_handler.handle_event(event, game)

        if state == 'menu':
            menu.draw()
        elif state == 'controls':
            controls.draw()
        else:
            renderers[0].draw_bg()
            for game, renderer, input_handler in zip(games, renderers, input_handlers):
                input_handler.update(game)
                renderer.draw_game(game)
        pygame.display.flip()
        clock.tick(240)


pygame.quit()
