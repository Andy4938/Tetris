import json
import pygame

class Keybinds:
    FILE = 'keybinds.json'
    # (action, label) in the order they're shown on the controls screen
    ACTIONS = [
        ('left', 'Move Left'),
        ('right', 'Move Right'),
        ('sd', 'Soft Drop'),
        ('hd', 'Hard Drop'),
        ('cw', 'Rotate CW'),
        ('ccw', 'Rotate CCW'),
        ('180', 'Rotate 180'),
        ('hold', 'Hold')
    ]
    DEFAULTS = {
        1: {
            'right': pygame.K_RIGHTBRACKET,
            'left': pygame.K_p,
            'hold': pygame.K_c,
            'cw': pygame.K_LEFTBRACKET,
            'ccw': pygame.K_z,
            '180': pygame.K_LSHIFT,
            'hd': pygame.K_SPACE,
            'sd': pygame.K_RALT
        },
        2: {
            'right': pygame.K_RIGHT,
            'left': pygame.K_LEFT,
            'hold': pygame.K_KP0,
            'cw': pygame.K_KP2,
            'ccw': pygame.K_KP1,
            '180': pygame.K_KP3,
            'hd': pygame.K_UP,
            'sd': pygame.K_DOWN
        }
    }
    # (setting, label, min, max, step) for handling, all values in ms
    HANDLING = [
        ('das', 'DAS', 0, 500, 5),
        ('arr', 'ARR', 0, 100, 1)
    ]
    HANDLING_DEFAULTS = {
        1: {'das': 75, 'arr': 0},
        2: {'das': 75, 'arr': 0}
    }
    # escape returns to the menu and r restarts the game, so they can't be bound
    RESERVED = (pygame.K_ESCAPE, pygame.K_r)

    def __init__(self):
        self.binds, self.handling = self._load()

    def get(self, player):
        return dict(self.binds[player])

    def get_handling(self, player):
        return dict(self.handling[player])

    def set(self, player, action, key):
        # binds key to player's action, swapping with whatever already used it
        # returns (other_player, other_action) if a swap happened, otherwise None
        swapped = None
        for other_player, binds in self.binds.items():
            for other_action, other_key in binds.items():
                if other_key == key and (other_player, other_action) != (player, action):
                    binds[other_action] = self.binds[player][action]
                    swapped = (other_player, other_action)
        self.binds[player][action] = key
        self.save()
        return swapped

    def set_handling(self, player, setting, value):
        self.handling[player][setting] = self.clamp_handling(setting, value)
        self.save()

    @classmethod
    def clamp_handling(cls, setting, value):
        for name, label, low, high, step in cls.HANDLING:
            if name == setting:
                return max(low, min(high, value))
        return value

    def reset(self):
        self.binds = {player: dict(binds) for player, binds in self.DEFAULTS.items()}
        self.handling = {player: dict(values) for player, values in self.HANDLING_DEFAULTS.items()}
        self.save()

    def save(self):
        try:
            with open(self.FILE, 'w') as file:
                json.dump({'binds': self.binds, 'handling': self.handling}, file, indent=4)
        except OSError:
            pass

    def _load(self):
        binds = {player: dict(defaults) for player, defaults in self.DEFAULTS.items()}
        handling = {player: dict(values) for player, values in self.HANDLING_DEFAULTS.items()}
        try:
            with open(self.FILE) as file:
                saved = json.load(file)
            saved_binds = saved.get('binds', saved)  # older files only stored binds at the top level
            saved_handling = saved.get('handling', {})
            for player in binds:
                for action in binds[player]:
                    key = saved_binds.get(str(player), {}).get(action)
                    if isinstance(key, int):
                        binds[player][action] = key
                for setting in handling[player]:
                    value = saved_handling.get(str(player), {}).get(setting)
                    if isinstance(value, int):
                        handling[player][setting] = self.clamp_handling(setting, value)
        except (OSError, ValueError, AttributeError):
            pass
        return binds, handling

    @staticmethod
    def key_name(key):
        name = pygame.key.name(key)
        if len(name) > 2 and name[0] == '[' and name[-1] == ']':  # pygame names numpad keys like [2]
            return f'Numpad {name[1:-1].title()}'
        return name.title() or 'Unknown'
