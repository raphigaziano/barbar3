"""
Client Constants

"""
from enum import Enum


SCREEN_W = 80
SCREEN_H = 70

MAP_VIEWPORT_W = SCREEN_W
MAP_VIEWPORT_H = 50
MAP_VIEWPORT_X = 0
MAP_VIEWPORT_Y = 0

STATS_CONSOLE_W = 25
STATS_CONSOLE_H = SCREEN_H - MAP_VIEWPORT_H - 1
STATS_CONSOLE_X = 0
STATS_CONSOLE_Y = SCREEN_H - STATS_CONSOLE_H

LOG_CONSOLE_W = SCREEN_W - STATS_CONSOLE_W
LOG_CONSOLE_H = SCREEN_H - MAP_VIEWPORT_H - 1
LOG_CONSOLE_X = SCREEN_W - LOG_CONSOLE_W
LOG_CONSOLE_Y = SCREEN_H - LOG_CONSOLE_H

MAX_MODAL_WIDTH = SCREEN_W - 20
MAX_MODAL_HEIGHT = MAP_VIEWPORT_H - 8

ASSETS_PATH = 'client_tcod/assets'

MAP_DEBUG = False
MAP_DEBUG_DELAY = 20.0

SHOW_UNEXPLORED_CELLS = False
SHOW_DEBUG_INFO = True
IGNORE_FOV = False

SHOW_PATH_INFO = False
SHOW_SPAWN_ZONES = False

IGNORE_FOV_ENTITY_TYPES = (
    'stairs',
)

AUTO_REST_N_TURNS = 50

class TileType(Enum):
    FLOOR = '.'
    WALL = '#'

import tcod

VI_KEYS = {
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

_MOVE_KEYS = {  # key_symbol: (x, y)
    # Arrow keys.
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    tcod.event.K_PERIOD: (0, 0),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    tcod.event.K_CLEAR: (0, 0),  # Numpad `clear` key.
}

MOVE_KEYS = _MOVE_KEYS | VI_KEYS
