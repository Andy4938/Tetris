class Board:
    def __init__(self, game_w, game_h, x, board_w, grid_thickness, border_thickness, fill_color, border_color):
        self.w = board_w
        self.h = board_w * 2
        self.x = x
        self.y = game_h - self.h - (game_h - self.h) / 2.5
        self.thickness = grid_thickness
        self.border_thickness = border_thickness
        self.border_color = border_color
        self.fill_color = fill_color
        self.matrix = [[None for _ in range(10)] for _ in range(40)]

