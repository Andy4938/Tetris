import pygame
import render
import random

pygame.init()
w = 1366
h = 768
board_width = 300
board_start_x = w / 2 - (board_width/ 2)
board_start_y = h / 1.8 - board_width
screen = pygame.display.set_mode((w, h))
clock = pygame.time.Clock()
running = True

def generate_7bag():
    pieces = ['i', 'o', 'j', 'l', 's', 't', 'z']
    queue = ''
    for i in range(7):
        index = random.randint(0, len(pieces) - 1)
        queue = queue + pieces[index]
        pieces.pop(index)
    return queue

queue = generate_7bag()
current = queue[0]
queue = queue[1:]
hold = ''
held = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                # print(held)
                if not held:
                    if not hold:
                        hold = current
                        current = queue[0]
                        queue = queue[1:]
                    else:
                        temp = current
                        current = hold
                        hold = temp
                    held = True
                    # print(current)
                    # print(hold)
    render.draw_bg(screen, w, h)
    render.draw_board(screen, board_start_x, board_start_y, board_width, board_width * 2, 3, 'black', (0, 0, 0))
    render.draw_queue(screen, board_start_x, board_start_y, board_width, board_width * 2, 30, hold, queue, current)

    pygame.display.flip()
    clock.tick(60)

