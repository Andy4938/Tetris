import pygame

def draw_bg(screen, width, height):
    screen.fill((255, 255, 255))
    bg_raw = pygame.image.load("bg.jpeg").convert()
    bg = pygame.transform.scale(bg_raw, (width, height))
    bg.set_alpha(200)
    screen.blit(bg, (0, 0))

def draw_board(screen, x, y, width, height, border_thickness, fill_color, border_color):
    # draw grid
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill(fill_color)
    grid_color = (107, 107, 107)
    cell_size = width / 10
    for row in range(1, 20):  # horizontal lines
        pygame.draw.line(surface, grid_color, (0, row * cell_size), (width, row * cell_size), 2)

    for col in range(1, 10):  # vertical lines
        pygame.draw.line(surface, grid_color, (col * cell_size, 0), (col * cell_size, height), 2)
    pygame.draw.rect(screen, 'white', (x - border_thickness, y - border_thickness, width + border_thickness * 2,
                                       height + border_thickness * 2))  # border
    screen.blit(surface, (x, y))

    # draw_hold_box
    hold_start_x = x - width / 2
    pygame.draw.rect(screen, 'white', (hold_start_x - border_thickness * 2, y - border_thickness, width / 2 + border_thickness * 2,
                                       height / 5.5 + border_thickness * 2))  # border
    pygame.draw.rect(screen, fill_color, (hold_start_x - border_thickness, y + 20, width / 2, height / 5.5 - 20))
    font_size = 32
    game_font = pygame.font.Font(None, font_size)
    hold_text_surface = game_font.render('Hold', True, 'black')
    screen.blit(hold_text_surface, (hold_start_x, y - 2))

    # draw queue
    q_start_x = x + width
    pygame.draw.rect(screen, 'white', (q_start_x, y - border_thickness, width / 2 + border_thickness * 2, height * 0.81 + border_thickness * 2))
    pygame.draw.rect(screen, 'black', (q_start_x + border_thickness, y + 20, width / 2, height * 0.81 - 20))
    next_text_surface = game_font.render('Next', True, 'black')
    screen.blit(next_text_surface, (q_start_x + 6, y - 2))

def draw_queue(screen, x, y, width, height, mino_size, hold, next, current):
    skin_raw = pygame.image.load("skin.png").convert()
    skin = pygame.transform.scale(skin_raw, (270, 30))
    pieces = ['p', 'g', 'z', 'l', 'o', 's', 'i', 'j', 't']
    piece_minos = { # represents filled in minos of a 3x2 grid, except I and O in a 4x2
    'z': [1, 1, 0, 0, 1, 1],
    'l': [0, 0, 1, 1, 1, 1],
    's': [0, 1, 1, 1, 1, 0],
    'j': [1, 0, 0, 1, 1, 1],
    't': [0, 1, 0, 1, 1, 1],
    'i': [0, 0, 0, 0, 1, 1, 1, 1],
    'o': [0, 1, 1, 0, 0, 1, 1, 0],
    }
    def draw_piece(screen, x, y, mino_size, piece):
        print(piece)
        crop_x = pieces.index(piece) * mino_size
        mino = pygame.Rect(crop_x, 0, mino_size, mino_size)
        mino_map = piece_minos[piece]
        if len(mino_map) == 6:
            for i in range(2):
                y_pos = i * mino_size
                for j in range(3):
                    x_pos = j * mino_size
                    if mino_map[i * 3 + j] == 1:
                        screen.blit(skin, (x + x_pos, y + y_pos), area=mino)
        if len(mino_map) == 8:
            for i in range(2):
                y_pos = i * mino_size
                for j in range(4):
                    x_pos = j * mino_size
                    if mino_map[i * 4 + j] == 1:
                         screen.blit(skin, (x + x_pos, y + y_pos), area=mino)
    # draw hold piece
    if hold:
        if hold == 'i' or hold == 'o':
            factor = 2 if hold == 'i' else 1
            draw_piece(screen, x - width * 0.46, y + 5 + mino_size / factor, 30, hold)
        else:
            draw_piece(screen, x - width * 0.415, y + mino_size + 5, 30, hold)

    # draw next pieces
    for index, piece in enumerate(next[:5]):
        offset = 18 if piece == 'i' or piece == 'o' else 34
        # factor = 2 if piece == 'i' else 1
        i_offset = 16 if piece == 'i' else 0
        draw_piece(screen, x + width + offset, y + 40 + mino_size * index * 3 - i_offset, 30, piece)

    # draw current piece
    draw_piece(screen, x + mino_size * 3 + 1, y - mino_size * 3 + 1, 30, current)

