class Board:
    def __init__(self, game_w, game_h, board_w, thickness, fill_color, border_color):
        self.w = board_w
        self.h = board_w * 2
        self.x = game_w / 2 - (self.w / 2)
        self.y = game_h - self.h - (game_h - self.h) / 3
        self.thickness = thickness
        self.border_color = border_color
        self.fill_color = fill_color

